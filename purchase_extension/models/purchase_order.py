from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date


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
        self.sale_partner_id = False
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

    @api.constrains('order_line')
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
            if self.env.user.has_group('purchase_extension.group_po_exceed_limit'):
                continue

            # Find Sale Order using po_reference (linked via origin or custom field)
            sale_order = self.env['sale.order'].search([('client_order_ref', '=', po.po_reference)], limit=1)
            if not sale_order:
                continue

            # Get all confirmed purchase orders with same po_reference
            confirmed_pos = self.env['purchase.order'].search([
                ('po_reference', '=', po.po_reference),
                ('state', 'in', ['purchase', 'done'])  # confirmed or done
            ])

            # Calculate total purchased quantities for each product
            purchased_qty_map = {}
            for existing_po in confirmed_pos:
                for line in existing_po.order_line:
                    purchased_qty_map[line.product_id.id] = purchased_qty_map.get(line.product_id.id, 0) + line.product_qty

            # Validate current PO lines
            for line in po.order_line:
                sale_line = sale_order.order_line.filtered(lambda l: l.product_id == line.product_id)
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
                        raise UserError(_(
                            "You cannot add more than the demanded quantity for product '%s' "
                            "in Sale Order '%s'.\n"
                            "Required: %s, Already Ordered: %s"
                        ) % (
                            line.product_id.display_name,
                            sale_order.name,
                            sale_qty,
                            already_purchased
                        ))
                    else:
                        raise UserError(_(
                            "You are trying to purchase more than the required quantity for product '%s' "
                            "in Sale Order '%s'.\n"
                            "Required: %s, Already Ordered: %s, Trying to Add: %s\n"
                            "You can only add: %s"
                        ) % (
                            line.product_id.display_name,
                            sale_order.name,
                            sale_qty,
                            already_purchased,
                            line.product_qty,
                            remaining_qty
                        ))

    # @api.model
    # def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, supplier, po):
    #     # Call the original method to get default values
    #     vals = super(PurchaseOrderLineInherit, self)._prepare_purchase_order_line(
    #         product_id, product_qty, product_uom, company_id, supplier, po
    #     )

    #     # Example: check if customer_id is available in PO or context
    #     customer = po.customer_id or self.env.context.get('customer_id')
    #     if customer:
    #         vals.update({'customer_id': customer.id})

    #     return vals

    # @api.model
    # def _prepare_purchase_order_line_from_procurement(
    #     self, product_id, product_qty, product_uom,
    #     location_dest_id, name, origin, company_id, values, po
    # ):
    #     res = super()._prepare_purchase_order_line_from_procurement(
    #         product_id, product_qty, product_uom,
    #         location_dest_id, name, origin, company_id, values, po
    #     )
    #     print("\n\n\n ---- values pol self ----", values)
    #     # Retrieve custom field
    #     if values.get('sr_no_so'):
    #         res['sr_no_po'] = values['sr_no_so']
    #     if values.get('sale_line_id'):
    #         res['sale_line_id'] = values['sale_line_id']
    #     return res
