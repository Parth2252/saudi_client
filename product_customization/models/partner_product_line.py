from odoo import models, fields

class PartnerProductLine(models.Model):
    _name = "partner.product.line"
    _description = "Partner Product Master Line"

    name = fields.Char(string="Name", required=True)
    product_id = fields.Many2one('product.product', string="Product")
    brand_id = fields.Many2one('product.brand', string="Brand")
    product_image = fields.Binary(string="Image")
    partner_id = fields.Many2one('res.partner', string="Partner")
