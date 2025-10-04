from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Purchase(models.Model):
    _inherit = "purchase.order"

    po_reference = fields.Char(string="PO Reference",copy=False)

    def _prepare_picking(self):
        res = super()._prepare_picking()
        res.update({
            'porder_ref': self.po_reference,
        })
        return res
