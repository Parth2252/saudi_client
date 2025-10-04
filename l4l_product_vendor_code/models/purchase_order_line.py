# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################


from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    vendor_product_name = fields.Char(string='Vendor Product Name')
    vendor_product_code = fields.Char(string='Vendor Product Code')
    enable_vendor_code_and_name = fields.Boolean(string="Enable Vendor Product Code and Name", compute="_compute_enable_vendor_code_and_name", store=False)

    @api.depends('order_id.company_id')
    def _compute_enable_vendor_code_and_name(self):
        for line in self:
            line.enable_vendor_code_and_name = line.order_id.company_id.enable_vendor_code_and_name

    @api.onchange('product_id', 'partner_id', 'product_qty', 'product_uom', 'company_id', 'order_id.partner_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id and line.partner_id:
                params = {'order_id': line.order_id._origin}
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(self),
                    uom_id=line.product_uom,
                    params=params)
                if seller:
                    line.vendor_product_name = seller.product_name
                    line.vendor_product_code = seller.product_code

    @api.onchange('vendor_product_name', 'vendor_product_code', 'price_unit', 'product_uom', 'product_qty', 'company_id', 'order_id.partner_id')
    def _onchange_vendor_product_info(self):
        for line in self:
            if line.product_id and line.partner_id:
                params = {'order_id': line.order_id._origin}
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(
                        self),
                    uom_id=line.product_uom,
                    params=params
                )
                if seller:
                    seller.product_name = line.vendor_product_name
                    seller.product_code = line.vendor_product_code
                else:
                    self.env['product.supplierinfo'].create({
                        'partner_id': line.partner_id.id,
                        'product_id': line.product_id.id,
                        'product_tmpl_id': line.product_id.product_tmpl_id.id,
                        'product_code': line.vendor_product_code,
                        'product_name': line.vendor_product_name,
                        'price': line.price_unit,
                        'currency_id': line.order_id.currency_id.id,
                        'min_qty': 1,
                    })

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res.update({
            'vendor_product_name': self.vendor_product_name,
            'vendor_product_code': self.vendor_product_code,
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
