# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def add_mass_product(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'add.mass.product.purchase',
            'view_mode': 'form',
            'target': 'new'
        }

    def import_from_file(self):
        wiz = self.env['import.from.file.purchase'].create({})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.from.file.purchase',
            'res_id': wiz.id,
            'view_mode': 'form',
            'target': 'new'
        }
