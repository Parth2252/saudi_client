# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import models, fields


class AddProductWizard(models.TransientModel):
    _name = 'add.mass.product.sale'
    _description = "Add Multiple Product"

    product_ids = fields.Many2many('product.product', domain=[('sale_ok', '=', True)])

    def add_product_wizard(self):
        order = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        lst = []
        for product in self.product_ids:
            lst.append((0, 0, {'product_id': product.id, 'name': product.name}))
        order.order_line = lst
