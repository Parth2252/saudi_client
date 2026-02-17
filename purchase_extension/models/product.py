from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_delivery_charge = fields.Boolean(string="Is Delivery Charge")


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_delivery_charge = fields.Boolean(
        related="product_tmpl_id.is_delivery_charge", readonly=False
    )
