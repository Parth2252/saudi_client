from odoo import models, fields, api, _, Command
import datetime
from datetime import timedelta
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang


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

    customer_pdd = fields.Datetime(string="Customer PDD", copy=False)

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
            line.customer_pdd = sale_line_id.delivery_date
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
            #     line.date_planned = po_date + timedelta(days=delay)
            # else:
            #     line.date_planned = fields.datetime.now()

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
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.order_id.purchase_source == "online" or (self.order_id.purchase_source == "standard" and self.order_id.currency_id.name != "SAR"):
            self.taxes_id = [Command.clear()]
        return res

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
            #     line.with_context(bypass_date_planned=True).write({
            #         'date_planned': new_date
            #     })
            # else:
            #     line.with_context(bypass_date_planned=True).write({
            #         'date_planned': fields.datetime.now()
            #     })

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

    @api.depends('product_qty', 'product_uom', 'company_id', 'order_id.partner_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        """ override method to set the false value in Expected Arrival Date """
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
            params = line._get_select_sellers_params()
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params)

            # if seller or not line.date_planned:
            #     line.date_planned = line._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            # If not seller, use the standard price. It needs a proper currency conversion.
            if not seller:
                line.discount = 0
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s: s.partner_id == line.order_id.partner_id)
                if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom:
                    # Avoid to modify the price unit if there is no price list for this partner and
                    # the line has already one to avoid to override unit price set manually.
                    continue
                po_line_uom = line.product_uom or line.product_id.uom_po_id
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(line.product_id.standard_price, po_line_uom),
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )
                price_unit = line.product_id.cost_currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False
                )
                line.price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places, self.env['decimal.precision'].precision_get('Product Price')))

            elif seller:
                price_unit = line.env['account.tax']._fix_tax_included_price_company(seller.price, line.product_id.supplier_taxes_id, line.taxes_id, line.company_id) if seller else 0.0
                price_unit = seller.currency_id._convert(price_unit, line.currency_id, line.company_id, line.date_order or fields.Date.context_today(line), False)
                price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places, self.env['decimal.precision'].precision_get('Product Price')))
                line.price_unit = seller.product_uom._compute_price(price_unit, line.product_uom)
                line.discount = seller.discount or 0.0

            # record product names to avoid resetting custom descriptions
            default_names = []
            vendors = line.product_id._prepare_sellers(params=params)
            product_ctx = {'seller_id': None, 'partner_id': None, 'lang': get_lang(line.env, line.partner_id.lang).code}
            default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
            for vendor in vendors:
                product_ctx = {'seller_id': vendor.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
            if not line.name or line.name in default_names:
                product_ctx = {'seller_id': seller.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                line.name = line._get_product_purchase_description(line.product_id.with_context(product_ctx))



