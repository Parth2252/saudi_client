# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from datetime import datetime

from odoo import models, fields


class AddProductWizard(models.TransientModel):
    _name = 'add.mass.product.purchase'
    _description = "Add Multiple Product"

    product_ids = fields.Many2many('product.product', domain=[('purchase_ok', '=', True)])

    def add_product_wizard(self):
        order = self.env['purchase.order'].browse(self.env.context.get('active_ids'))
        lst = []
        for product in self.product_ids:
            lst.append((0, 0, {'product_id': product.id, 'name': product.name, 'price_unit': product.lst_price, 'product_qty': 1, 'date_planned': datetime.today(), 'product_uom': product.uom_po_id.id}))
        order.order_line = lst
