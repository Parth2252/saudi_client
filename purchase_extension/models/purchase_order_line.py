from odoo import models, fields, api, _
import datetime
from datetime import timedelta


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    ts_code = fields.Char(
        string="TS Code", related="product_id.default_code", store=True, readonly=False
    )
    product_code = fields.Char(
        "Vendor Product Code",
        help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.",
    )
    sr_no_po = fields.Integer(string="Order No")

    product_url = fields.Char(string="Product URL")

    def purchase_order_line_sequence(self):
        """ Generate auto sequence for purchase order. """
        number = 1
        for record in self.order_id.order_line:
            if not record.display_type:
                record.sr_no_po = number
                number += 1

    @api.model
    def create(self, vals):
        new_product_id = False
        sr_no_po_value = False

        sale_line_id = vals.get('sale_line_id')
        move_dest_ids = vals.get('move_dest_ids', [])

        move = False
        if move_dest_ids:
            move_id = move_dest_ids[0][1]
            move = self.env['stock.move'].browse(move_id)

        if sale_line_id:
            sale_line = self.env['sale.order.line'].browse(sale_line_id)
            if sale_line:
                sr_no_po_value = sale_line.sr_no_so
                if sale_line.offered_description_id:
                    new_product_id = sale_line.offered_description_id
        else:
            if move and move.sale_line_id:
                sale_line_id = move.sale_line_id
                sr_no_po_value = move.sale_line_id.sr_no_so
                if move.sale_line_id.offered_description_id:
                    new_product_id = move.sale_line_id.offered_description_id

        if sale_line_id:
            vals['sale_line_id'] = sale_line_id.id

        if new_product_id:
            vals['product_id'] = new_product_id.id
            vals['name'] = new_product_id.name

        po = self.env['purchase.order'].browse(vals.get('order_id'))
        partner = po.partner_id

        product = new_product_id or self.env['product.product'].browse(vals.get('product_id'))

        if product:
            supplierinfo = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('partner_id', '=', partner.id)
            ], limit=1)

            if supplierinfo:
                vals['price_unit'] = supplierinfo.price

        line = super(PurchaseOrderLine, self).create(vals)
        if sale_line_id:
            line.product_url = sale_line_id.product_url
            line.product_uom = sale_line_id.product_uom.id
        if sr_no_po_value:
            line.sr_no_po = sr_no_po_value

        if not sale_line_id and not (move and move.sale_line_id):
            line.purchase_order_line_sequence()

        for line in self:
            partner = line.order_id.partner_id
            product = line.product_id

            if not product or not partner:
                continue

            # Find supplierinfo
            supplierinfo = self.env['product.supplierinfo'].search([
                ('product_id', '=', product.id),
                ('partner_id', '=', partner.id)
            ], limit=1)

            if supplierinfo:
                delay = supplierinfo.delay or 0   # delay in days
                po_date = line.order_id.date_order or fields.Date.today()

                # Convert to date (date_order may be datetime)
                if isinstance(po_date, datetime.datetime):
                    po_date = po_date.date()

                # Expected Arrival = PO Date + Delay
                line.date_planned = po_date + timedelta(days=delay)
            else:
                line.date_planned = False

        return line

    @api.onchange("product_id", "partner_id")
    def onchange_product_id(self):
        if self.product_id:
            model_id = self.env.ref("purchase.model_purchase_order_line")
            fields_list = model_id.field_id.mapped("name")
            product_supplier = self.env["product.supplierinfo"].search(
                [
                    ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
                    ("partner_id", "=", self.partner_id.id),
                ],
                limit=1,
            )
            if product_supplier:
                self.product_code = product_supplier.product_code
            else:
                self.product_code = 0.0
        return super(PurchaseOrderLine, self).onchange_product_id()

    def write(self, vals):
        # If bypass flag is set, skip logic to avoid recursion
        if self.env.context.get("bypass_date_planned"):
            return super(PurchaseOrderLine, self).write(vals)

        res = super(PurchaseOrderLine, self).write(vals)

        for line in self:
            partner = line.order_id.partner_id
            product = line.product_id

            if not partner or not product:
                continue

            supplierinfo = self.env['product.supplierinfo'].search([
                ('product_id', '=', product.id),
                ('partner_id', '=', partner.id)
            ], limit=1)

            if supplierinfo:
                delay = supplierinfo.delay or 0
                po_date = line.order_id.date_order or fields.Date.today()

                # Convert datetime to date
                if isinstance(po_date, datetime.datetime):
                    po_date = po_date.date()

                new_date = po_date + timedelta(days=delay)

                # Write WITHOUT recursion using context flag
                line.with_context(bypass_date_planned=True).write({
                    'date_planned': new_date
                })
            else:
                line.with_context(bypass_date_planned=True).write({
                    'date_planned': False
                })

        return res

    def _prepare_stock_moves(self, picking):
        vals_list = super()._prepare_stock_moves(picking)

        # Ensure we always have a list
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        for vals in vals_list:
            if isinstance(vals, dict):   # Prevent boolean crash
                vals['date'] = self.date_planned or fields.Datetime.now()

        return vals_list


