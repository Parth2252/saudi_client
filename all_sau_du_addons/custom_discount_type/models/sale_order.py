from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')
    ], string='Discount Type', default='percentage')

    fixed_discount_value = fields.Float(string="Discount Value")

    @api.onchange('discount_type', 'fixed_discount_value', 'price_unit', 'product_uom_qty')
    def _onchange_discount_type(self):
        for line in self:
            if line.discount_type == 'fixed' and line.product_uom_qty and line.price_unit:
                per_unit_discount = line.fixed_discount_value / line.product_uom_qty
                percent_discount = (per_unit_discount / line.price_unit) * 100
                line.discount = percent_discount
            elif line.discount_type == 'percentage':
                line.discount = line.fixed_discount_value

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update({
            'discount_type': self.discount_type,
            'fixed_discount_value': self.fixed_discount_value,
        })
        return res