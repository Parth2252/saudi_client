from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError, UserError
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tools import format_amount, format_date, format_list, formatLang, groupby


class PurchaseAttachmentType(models.Model):
    _name = "purchase.attachment.type"
    _description = "Purchase Attachment Type"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color Index")


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_default_customer_contact_id(self):
        return self.env["res.partner"].search(
            [("name", "=", "TAMSTAR TRADING ESTABLISHMENT")], limit=1
        )

    def _get_default_partner_invoice_id(self):
        contact = self._get_default_customer_contact_id()
        if contact:
            return contact.address_get(["invoice"])["invoice"]
        return False

    def _get_default_partner_shipping_id(self):
        contact = self._get_default_customer_contact_id()
        if contact:
            return contact.address_get(["delivery"])["delivery"]
        return False

    date_planned = fields.Datetime(
        string='Expected Arrival', index=True, copy=False, store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")

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
    customer_contact_id = fields.Many2one(
        "res.partner",
        string="Customer Contact",
        check_company=True,
        default=_get_default_customer_contact_id,
    )
    partner_invoice_id = fields.Many2one(
        "res.partner",
        string="Partner Invoice Address",
        check_company=True,
        default=_get_default_partner_invoice_id,
    )
    partner_shipping_id = fields.Many2one(
        "res.partner",
        string="Partner Shipping Address",
        check_company=True,
        default=_get_default_partner_shipping_id,
    )

    @api.onchange("customer_contact_id")
    def _onchange_customer_contact_id(self):
        if self.customer_contact_id:
            addr = self.customer_contact_id.address_get(["delivery", "invoice"])
            self.partner_invoice_id = addr["invoice"]
            self.partner_shipping_id = addr["delivery"]
        else:
            self.partner_invoice_id = False
            self.partner_shipping_id = False

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

    order_confirmation_number = fields.Char(string="Order Confirmation Number")

    order_status = fields.Selection(
        [
            ("acknowledged", "Order Acknowledged by vendor"),
            ("shipped", "order shipped"),
        ],
        string="Order status",
    )
    attachment_type_ids = fields.Many2many(
        "purchase.attachment.type",
        string="Attachment Type",
        required=True,
    )

    tracking_number = fields.Char(string="Tracking Number")
    logistic_name = fields.Char(string="Logistic Name")
    logistic_url = fields.Char(string="Logistic URL")

    is_confirmation_filled = fields.Boolean(
        compute="_compute_is_confirmation_filled", string="Is Confirmation Filled"
    )

    @api.depends("order_confirmation_number")
    def _compute_is_confirmation_filled(self):
        for rec in self:
            rec.is_confirmation_filled = bool(rec.order_confirmation_number)

    receipt_delay = fields.Integer(
        string="Receipt Delay (Days)", compute="_compute_receipt_delay", store=True
    )

    po_status = fields.Selection(
        [
            ("to_issue", "To Issue (PO/Order)"),
            ("ordered", "Ordered(Purchase Order)"),
            ("acknowledged", "Order Acknowledged"),
            ("shipped", "Order Shipped"),
            ("material_delay", "Delayed/Receipt Delay"),
            ("received", "Received (Totally)"),
            ("pending_bill", "Pending Vendor Bill"),
            ("bill_not_paid", "Bill Not Paid"),
            ("paid_not_received", "Bill Paid/Material not Received"),
        ],
        string="PO Status",
        compute="_compute_po_status",
        store=True,
    )

    @api.depends(
        "state",
        "po_reference",
        "invoice_ids",
        "invoice_ids.payment_state",
        "invoice_ids.state",
        "picking_ids",
        "picking_ids.state",
        "receipt_delay",
        "purchase_source",
        "order_confirmation_number",
        "order_status",
    )
    def _compute_po_status(self):
        for order in self:
            status = False
            if order.state in ("draft", "sent"):
                status = "to_issue"
            elif order.state in ("purchase", "done"):
                invoices = order.invoice_ids
                pickings = order.picking_ids

                if order.purchase_source == 'online':
                    # Online Flow Logic
                    all_received = pickings and all(p.state in ("done", "delivered") for p in pickings)

                    if all_received:
                        status = "received"
                    elif order.receipt_delay > 0:
                        status = "material_delay"
                    elif order.order_status == 'shipped':
                        status = "shipped"
                    elif order.order_status == 'acknowledged':
                        status = "acknowledged"
                    elif order.order_confirmation_number:
                        status = "ordered"
                    else:
                        status = "ordered" # Default for confirmed online
                else:
                    # Standard/Local Flow Logic
                    is_paid = any(inv.payment_state == "paid" for inv in invoices)
                    bill_not_paid = invoices and any(inv.state != 'draft' and inv.payment_state != 'paid' for inv in invoices)
                    pending_bill = not invoices or any(inv.state == "draft" for inv in invoices)

                    if is_paid and any(p.state in ("done", "delivered") for p in pickings) and order.receipt_delay > 0:
                        status = "material_delay"
                    elif is_paid and (not pickings or any(p.state in ("waiting", "assigned", "confirmed") for p in pickings)):
                        status = "paid_not_received"
                    elif bill_not_paid:
                        status = "bill_not_paid"
                    elif pending_bill:
                        status = "pending_bill"
                    else:
                        status = "ordered"
            order.po_status = status

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            purchase_source = vals.get("purchase_source")
            currency_id = vals.get("currency_id")
            currency_name = self.env['res.currency'].browse(currency_id).name if currency_id else False

            # Tax removal condition
            remove_taxes = purchase_source == "online" or (purchase_source == "standard" and currency_name and currency_name != "SAR")

            if remove_taxes:
                order_lines = vals.get("order_line", [])
                for line in order_lines:
                    if (
                        isinstance(line, (list, tuple))
                        and len(line) >= 3
                        and line[0] in [Command.CREATE, Command.UPDATE]
                    ):
                        line[2]["taxes_id"] = [Command.set([])]

            if purchase_source == "online":
                delivery_product = (
                    self.env["product.product"]
                    .sudo()
                    .search([("is_delivery_charge", "=", True)], limit=1)
                )
                if delivery_product:
                    order_lines = vals.get("order_line", [])
                    has_delivery = False
                    for line in order_lines:
                        if (
                            isinstance(line, (list, tuple))
                            and len(line) >= 3
                            and line[0] == Command.CREATE
                            and line[2].get("product_id") == delivery_product.id
                        ):
                            has_delivery = True

                    if not has_delivery:
                        vals.setdefault("order_line", []).append(
                            Command.create(
                                {
                                    "product_id": delivery_product.id,
                                    "product_qty": 1,
                                    "taxes_id": [Command.set([])] if remove_taxes else False
                                }
                            )
                        )
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get("skip_delivery_charge"):
            return res
        for order in self:
            if order.purchase_source == "online":
                delivery_product = (
                    self.env["product.product"]
                    .sudo()
                    .search([("is_delivery_charge", "=", True)], limit=1)
                )
                if delivery_product:
                    if not any(
                        line.product_id == delivery_product
                        for line in order.order_line
                    ):
                        order.with_context(skip_delivery_charge=True).write(
                            {
                                "order_line": [
                                    Command.create(
                                        {
                                            "product_id": delivery_product.id,
                                            "product_qty": 1,
                                        }
                                    )
                                ]
                            }
                        )

            if order.purchase_source == "online" or (order.purchase_source == "standard" and order.currency_id.name != "SAR"):
                # Automatically remove taxes for all lines if it's an online order or standard order with non-SAR currency
                lines_to_clear_taxes = order.order_line.filtered(lambda l: l.taxes_id)
                if lines_to_clear_taxes:
                    lines_to_clear_taxes.with_context(skip_delivery_charge=True).write(
                        {"taxes_id": [Command.clear()]}
                    )
        return res

    @api.onchange("purchase_source", "currency_id")
    def _onchange_purchase_source_currency_clear_taxes(self):
        if self.purchase_source == "online" or (self.purchase_source == "standard" and self.currency_id.name != "SAR"):
            for line in self.order_line:
                line.taxes_id = [Command.clear()]

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

    @api.constrains("purchase_source", "order_line")
    def _check_product_url(self):
        """
        Validates that all purchase order lines have a product URL when the
        purchase source is set to 'online'. Displays all missing products in one message.
        """
        if self.env.context.get("skip_product_url_check"):
            return
        for order in self:
            if order.purchase_source == "online":
                missing_url_products = []
                for line in order.order_line:
                    if not line.display_type and not line.product_url and not line.product_id.is_delivery_charge:
                        missing_url_products.append(line.product_id.display_name)

                if missing_url_products:
                    products_str = "\n\n- " + "\n- ".join(missing_url_products)
                    raise ValidationError(
                        _(
                            "Product URL is required for the following products when Purchase Source is 'Online Purchase':%s"
                        )
                        % products_str
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
        result["standard_purchase_to_issues"] = po.search_count([("po_status", "=", "to_issue"), ("purchase_source", "=", "standard")])
        result["standard_purchase_ordered"] = po.search_count([("po_status", "=", "ordered"), ("purchase_source", "=", "standard")])
        result["standard_purchase_pending_bill"] = po.search_count([("po_status", "=", "pending_bill"), ("purchase_source", "=", "standard")])
        result["standard_purchase_bill_not_paid"] = po.search_count([("po_status", "=", "bill_not_paid"), ("purchase_source", "=", "standard")])
        result["standard_purchase_bill_paid_not_received"] = po.search_count([("po_status", "=", "paid_not_received"), ("purchase_source", "=", "standard")])
        result["standard_purchase_receipt_delay"] = po.search_count([("po_status", "=", "material_delay"), ("purchase_source", "=", "standard")])
        # Standard Purchase order customization end

        # Local Purchase order Customization start.
        result["local_purchase_to_issues"] = po.search_count([("po_status", "=", "to_issue"), ("purchase_source", "=", "local")])
        result["local_purchase_ordered"] = po.search_count([("po_status", "=", "ordered"), ("purchase_source", "=", "local")])
        result["local_purchase_pending_bill"] = po.search_count([("po_status", "=", "pending_bill"), ("purchase_source", "=", "local")])
        result["local_purchase_bill_not_paid"] = po.search_count([("po_status", "=", "bill_not_paid"), ("purchase_source", "=", "local")])
        result["local_purchase_bill_paid_not_received"] = po.search_count([("po_status", "=", "paid_not_received"), ("purchase_source", "=", "local")])
        result["local_purchase_receipt_delay"] = po.search_count([("po_status", "=", "material_delay"), ("purchase_source", "=", "local")])
        # Local Purchase order customization end

        # Online Purchase order        # Online Purchase
        result["online_purchase_to_order"] = po.search_count([("po_status", "=", "to_issue"), ("purchase_source", "=", "online")])
        result["online_purchase_ordered"] = po.search_count([("po_status", "=", "ordered"), ("purchase_source", "=", "online")])
        result["online_purchase_acknowledged"] = po.search_count([("po_status", "=", "acknowledged"), ("purchase_source", "=", "online")])
        result["online_purchase_shipped"] = po.search_count([("po_status", "=", "shipped"), ("purchase_source", "=", "online")])
        result["online_purchase_delayed"] = po.search_count([("po_status", "=", "material_delay"), ("purchase_source", "=", "online")])
        result["online_purchase_received"] = po.search_count([("po_status", "=", "received"), ("purchase_source", "=", "online")])
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
        result["is_po_view"] = self.env.context.get('is_po_view', False)

        return result

    def _prepare_picking(self):
        res = super()._prepare_picking()
        res.update({'purchase_source':self.purchase_source})
        return res

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update({'purchase_source':self.purchase_source})
        return res

    def button_confirm(self):
        for order in self:
            errors = []
            if not order.purchase_source:
                errors.append(_("Purchase Source"))
            if not order.po_reference:
                errors.append(_("PO Reference"))
            if not order.sale_partner_id:
                errors.append(_("Sale Customer"))
            if not order.user_id:
                errors.append(_("Buyer"))
            if not order.attachment_type_ids:
                errors.append(_("Attachment Type"))
            if not order.date_planned:
                errors.append(_("Expected Arrival Date"))

            missing_pdd_products = []
            for line in order.order_line:
                if not line.display_type and not line.customer_pdd and not line.product_id.is_delivery_charge:
                    missing_pdd_products.append(line.product_id.display_name)

            if errors or missing_pdd_products:
                msg = _("Please provide values for the following missing fields before confirming:")
                if errors:
                    msg += "\n\n" + _("Header Fields:")
                    for error in errors:
                        msg += f"\n- {error}"
                
                if missing_pdd_products:
                    msg += "\n\n" + _("Customer PDD for Products:")
                    for product_name in missing_pdd_products:
                        msg += f"\n- {product_name}"
                
                raise ValidationError(msg)

        return super(PurchaseOrder, self).button_confirm()

    def action_add_confirmation_number(self):
        self.ensure_one()
        return {
            "name": "Add Order Confirmation Number",
            "type": "ir.actions.act_window",
            "res_model": "order.confirmation.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id},
        }

    def action_add_order_status(self):
        self.ensure_one()
        return {
            "name": "Update Order Status",
            "type": "ir.actions.act_window",
            "res_model": "order.status.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_order_id": self.id,
                "default_order_status": self.order_status,
                "default_tracking_number": self.tracking_number,
            },
        }

    def action_open_new_rfq_wizard(self):
        self.ensure_one()
        return {
            "name": "Create New RFQ",
            "type": "ir.actions.act_window",
            "res_model": "create.new.rfq.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_purchase_id": self.id},
        }