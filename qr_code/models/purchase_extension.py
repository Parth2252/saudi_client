# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_picking(self):
        res = super()._prepare_picking()
        return {
            **res,
            'user_id': self.env.user.id,
        }
