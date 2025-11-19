from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tools import format_amount, format_date, format_list, formatLang, groupby


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_is_overdue", store=True
    )
    sale_partner_id = fields.Many2one(
        "res.partner",
        string="Sale Customer",
        required=False,
        change_default=True,
        tracking=True,
        check_company=True,
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.",
    )

    print_vendor_item_code_and_name = fields.Boolean(copy=False)

    # NEW
    date_order_display = fields.Char(
        string="Delivery Time", compute="_compute_date_order_display"
    )
    contact_id = fields.Many2one("res.partner", "Customer Contact", readonly=True)

    # Added new field.
    po_expire_date = fields.Datetime(copy=False)

    purchase_source = fields.Selection(
        [
            ("standard", "Standard Purchase"),
            ("local", "Local Purchase"),
            ("online", "Online Purchase"),
        ],
        string="Purchase Source",
    )

    receipt_delay = fields.Integer(
        string="Receipt Delay (Days)", compute="_compute_receipt_delay", store=True
    )

    @api.depends("date_planned", "picking_ids.scheduled_date")
    def _compute_receipt_delay(self):
        for order in self:
            delay = 0
            # Take earliest scheduled date (PO level)
            planned_date = order.date_planned

            # Find the incoming picking (only receipts)
            pickings = order.picking_ids.filtered(
                lambda p: p.picking_type_id.code == "incoming"
            )

            if planned_date and pickings:
                # Find latest completion date among receipts
                done_pickings = pickings.filtered(lambda p: p.state == "done")
                if done_pickings:
                    scheduled_date = max(
                        done_pickings.mapped("scheduled_date")
                    )  # timezone safe

                    # Calculate delay (in days)
                    delay = (scheduled_date.date() - planned_date.date()).days

            order.receipt_delay = delay if delay > 0 else 0

    @api.depends("date_order")
    def _compute_date_order_display(self):
        for rec in self:
            if rec.date_order:
                delta_days = abs((rec.date_order.date() - date.today()).days)

                if delta_days == 0:
                    rec.date_order_display = "Today"
                elif delta_days >= 7:
                    weeks = delta_days // 7
                    rec.date_order_display = f"{weeks} WEEK{'S' if weeks > 1 else ''}"
                elif delta_days < 7:
                    if delta_days <= 1:
                        day = (rec.date_order.date() - date.today()).days
                        if day < 1:
                            rec.date_order_display = f"{'Yesterday'}"
                        if day >= 1:
                            rec.date_order_display = f"{'Tomorrow'}"
                    else:
                        rec.date_order_display = (
                            f"{delta_days} DAY{'S' if delta_days > 1 else ''}"
                        )
            else:
                rec.date_order_display = "False"

    # NEW

    def _get_sale_orders(self):
        res = super(PurchaseOrder, self)._get_sale_orders()

        linked_so = (
            self.order_line.move_dest_ids.group_id.sale_id
            | self.env["stock.move"]
            .browse(self.order_line.move_ids._rollup_move_dests())
            .group_id.sale_id
        )
        group_so = self.order_line.group_id.sale_id
        # self.sale_partner_id = False
        if linked_so or group_so:
            self.sale_partner_id = linked_so[0].partner_id or group_so[0].partner_id
        return super()._get_sale_orders() | linked_so | group_so

    @api.depends("date_order", "date_planned")
    def _compute_is_overdue(self):
        for order in self:
            order.is_overdue = (
                order.date_order
                and order.date_order < fields.Datetime.today()
                and order.state not in ("done", "cancel")
            )

    @api.constrains("order_line")
    def _check_po_quantities_against_so(self):
        """
        Validates purchase order line quantities against the corresponding Sale Order demand.

        This constraint ensures that the cumulative quantities of products ordered through purchase orders
        linked to the same sale order (via the `origin` or `po_reference`) do not exceed the quantities
        specified in the sale order lines.

        Behavior:
            - Retrieves the related Sale Order using the purchase order's `origin` field.
            - Aggregates the total quantities already ordered for each product across all
              confirmed purchase orders (`purchase`, `done`) linked to the same sale order.
            - Validates each product line in the current purchase order:
                • If the new total (already ordered + current PO line) exceeds the sale order quantity:
                    – If the remaining quantity is greater than 0:
                        Raises a UserError showing the allowed remaining quantity.
                    – If the remaining quantity is 0:
                        Raises a UserError indicating that no additional quantity can be ordered.

        Raises:
            UserError: If any product line exceeds the demanded quantity from the Sale Order.

        Example message when remaining quantity > 0:
            "You are trying to purchase more than the required quantity for product 'Product A'
            in Sale Order 'SO023'.
            Required: 10, Already Ordered: 7, Trying to Add: 5
            You can only add: 3"

        Example message when remaining quantity = 0:
            "You cannot add more than the demanded quantity for product 'Product A'
            in Sale Order 'SO023'.
            Required: 10, Already Ordered: 10"
        """
        for po in self:
            if not po.po_reference:  # Assuming origin contains Sale Order reference
                continue

            # Skip validation if user has special rights
            if self.env.user.has_group("purchase_extension.group_po_exceed_limit"):
                continue

            # Find Sale Order using po_reference (linked via origin or custom field)
            sale_order = self.env["sale.order"].search(
                [("client_order_ref", "=", po.po_reference)], limit=1
            )
            if not sale_order:
                continue

            # Get all confirmed purchase orders with same po_reference
            confirmed_pos = self.env["purchase.order"].search(
                [
                    ("po_reference", "=", po.po_reference),
                    ("state", "in", ["purchase", "done"]),  # confirmed or done
                ]
            )

            # Calculate total purchased quantities for each product
            purchased_qty_map = {}
            for existing_po in confirmed_pos:
                for line in existing_po.order_line:
                    purchased_qty_map[line.product_id.id] = (
                        purchased_qty_map.get(line.product_id.id, 0) + line.product_qty
                    )

            # Validate current PO lines
            for line in po.order_line:
                sale_line = sale_order.order_line.filtered(
                    lambda l: l.product_id == line.product_id
                )
                if not sale_line:
                    continue

                # calculate required qty using loop
                sale_qty = 0
                for sl in sale_line:
                    sale_qty += sl.product_uom_qty

                already_purchased = purchased_qty_map.get(line.product_id.id, 0)
                remaining_qty = max(sale_qty - already_purchased, 0)

                # Calculate new total after adding this PO
                new_total = already_purchased + line.product_qty
                if new_total > sale_qty:
                    if remaining_qty <= 0:
                        raise UserError(
                            _(
                                "You cannot add more than the demanded quantity for product '%s' "
                                "in Sale Order '%s'.\n"
                                "Required: %s, Already Ordered: %s"
                            )
                            % (
                                line.product_id.display_name,
                                sale_order.name,
                                sale_qty,
                                already_purchased,
                            )
                        )
                    else:
                        raise UserError(
                            _(
                                "You are trying to purchase more than the required quantity for product '%s' "
                                "in Sale Order '%s'.\n"
                                "Required: %s, Already Ordered: %s, Trying to Add: %s\n"
                                "You can only add: %s"
                            )
                            % (
                                line.product_id.display_name,
                                sale_order.name,
                                sale_qty,
                                already_purchased,
                                line.product_qty,
                                remaining_qty,
                            )
                        )

    @api.model
    def retrieve_dashboard(self):
        """Overide this function returns the values to populate the custom dashboard in
        the purchase order views.
        """
        self.browse().check_access("read")

        result = {
            "all_to_send": 0,
            "all_waiting": 0,
            "all_late": 0,
            "my_to_send": 0,
            "my_waiting": 0,
            "my_late": 0,
            "all_avg_order_value": 0,
            "all_avg_days_to_purchase": 0,
            "all_total_last_7_days": 0,
            "all_sent_rfqs": 0,
            "company_currency_symbol": self.env.company.currency_id.symbol,
        }

        one_week_ago = fields.Datetime.to_string(
            fields.Datetime.now() - relativedelta(days=7)
        )

        query = """SELECT COUNT(1)
                   FROM mail_message m
                   JOIN purchase_order po ON (po.id = m.res_id)
                   WHERE m.create_date >= %s
                     AND m.model = 'purchase.order'
                     AND m.message_type = 'notification'
                     AND m.subtype_id = %s
                     AND po.company_id = %s;
                """

        self.env.cr.execute(
            query,
            (
                one_week_ago,
                self.env.ref("purchase.mt_rfq_sent").id,
                self.env.company.id,
            ),
        )
        res = self.env.cr.fetchone()
        result["all_sent_rfqs"] = res[0] or 0

        # easy counts
        po = self.env["purchase.order"]
        result["all_to_send"] = po.search_count([("state", "=", "draft")])
        result["my_to_send"] = po.search_count(
            [("state", "=", "draft"), ("user_id", "=", self.env.uid)]
        )
        result["all_waiting"] = po.search_count(
            [("state", "=", "sent"), ("date_order", ">=", fields.Datetime.now())]
        )
        result["my_waiting"] = po.search_count(
            [
                ("state", "=", "sent"),
                ("date_order", ">=", fields.Datetime.now()),
                ("user_id", "=", self.env.uid),
            ]
        )
        result["all_late"] = po.search_count(
            [
                ("state", "in", ["draft", "sent", "to approve"]),
                ("date_order", "<", fields.Datetime.now()),
            ]
        )
        result["my_late"] = po.search_count(
            [
                ("state", "in", ["draft", "sent", "to approve"]),
                ("date_order", "<", fields.Datetime.now()),
                ("user_id", "=", self.env.uid),
            ]
        )

        # Standard Purchase order Customization start.
        result["standard_purchase_to_issues"] = po.search_count(
            [
                ("state", "in", ("draft", "sent")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "standard"),
            ]
        )
        result["standard_purchase_pending_bill"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "standard"),
                "|",
                ("invoice_ids", "=", False),
                ("invoice_ids.state", "=", "draft"),
            ]
        )
        result["standard_purchase_bill_paid_not_received"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "standard"),
                ("invoice_ids.payment_state", "=", "paid"),
                "|",
                ("picking_ids", "=", False),
                ("picking_ids.state", "in", ("waiting", "assigned", "confirmed")),
            ]
        )
        result["standard_purchase_receipt_delay"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "standard"),
                ("invoice_ids.payment_state", "=", "paid"),
                ("picking_ids.state", "in", ("done", "delivered")),
                ("receipt_delay", ">", 0),
            ]
        )
        # Standard Purchase order customization end

        # Local Purchase order Customization start.
        result["local_purchase_to_issues"] = po.search_count(
            [
                ("state", "in", ("draft", "sent")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "local"),
            ]
        )
        result["local_purchase_pending_bill"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "local"),
                "|",
                ("invoice_ids", "=", False),
                ("invoice_ids.state", "=", "draft"),
            ]
        )
        result["local_purchase_bill_paid_not_received"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "local"),
                ("invoice_ids.payment_state", "=", "paid"),
                "|",
                ("picking_ids", "=", False),
                ("picking_ids.state", "in", ("waiting", "assigned", "confirmed")),
            ]
        )
        result["local_purchase_receipt_delay"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "local"),
                ("invoice_ids.payment_state", "=", "paid"),
                ("picking_ids.state", "in", ("done", "delivered")),
                ("receipt_delay", ">", 0),
            ]
        )
        # Local Purchase order customization end

        # Online Purchase order Customization start.
        result["online_purchase_to_issues"] = po.search_count(
            [
                ("state", "in", ("draft", "sent")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "online"),
            ]
        )
        result["online_purchase_pending_bill"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "online"),
                "|",
                ("invoice_ids", "=", False),
                ("invoice_ids.state", "=", "draft"),
            ]
        )
        result["online_purchase_bill_paid_not_received"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "online"),
                ("invoice_ids.payment_state", "=", "paid"),
                "|",
                ("picking_ids", "=", False),
                ("picking_ids.state", "in", ("waiting", "assigned", "confirmed")),
            ]
        )
        result["online_purchase_receipt_delay"] = po.search_count(
            [
                ("state", "in", ("purchase", "done")),
                ("po_reference", "!=", False),
                ("purchase_source", "=", "online"),
                ("invoice_ids.payment_state", "=", "paid"),
                ("picking_ids.state", "in", ("done", "delivered")),
                ("receipt_delay", ">", 0),
            ]
        )
        # Online Purchase order customization end

        # Calculated values ('avg order value', 'avg days to purchase', and 'total last 7 days') note that 'avg order value' and
        # 'total last 7 days' takes into account exchange rate and current company's currency's precision.
        # This is done via SQL for scalability reasons
        query = """SELECT AVG(COALESCE(po.amount_total / NULLIF(po.currency_rate, 0), po.amount_total)),
                          AVG(extract(epoch from age(po.date_approve,po.create_date)/(24*60*60)::decimal(16,2))),
                          SUM(CASE WHEN po.date_approve >= %s THEN COALESCE(po.amount_total / NULLIF(po.currency_rate, 0), po.amount_total) ELSE 0 END)
                   FROM purchase_order po
                   WHERE po.state in ('purchase', 'done')
                     AND po.company_id = %s
                """
        self._cr.execute(query, (one_week_ago, self.env.company.id))
        res = self.env.cr.fetchone()
        result["all_avg_days_to_purchase"] = round(res[1] or 0, 2)
        currency = self.env.company.currency_id
        result["all_avg_order_value"] = format_amount(self.env, res[0] or 0, currency)
        result["all_total_last_7_days"] = format_amount(self.env, res[2] or 0, currency)

        return result
