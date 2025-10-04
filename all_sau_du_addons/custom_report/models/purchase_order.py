from odoo import api, Command, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    u_pr_char = fields.Char(string="Unit Price")

