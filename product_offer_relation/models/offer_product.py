from odoo import models, fields

class ProductOfferLine(models.Model):
    _name = 'product.offer.line'
    _description = 'Offer Product Line'

    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Offer Product", required=True)
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", copy=False)

