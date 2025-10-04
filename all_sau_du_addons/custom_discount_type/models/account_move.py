from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')
    ], string='Discount Type', default='percentage')

    fixed_discount_value = fields.Float(string="Discount Value")

    @api.onchange('discount_type', 'fixed_discount_value', 'price_unit', 'quantity')
    def _onchange_discount_type(self):
        for line in self:
            if line.discount_type == 'fixed' and line.quantity and line.price_unit:
                per_unit_discount = line.fixed_discount_value / line.quantity
                percent_discount = (per_unit_discount / line.price_unit) * 100
                line.discount = percent_discount
            elif line.discount_type == 'percentage':
                line.discount = line.fixed_discount_value