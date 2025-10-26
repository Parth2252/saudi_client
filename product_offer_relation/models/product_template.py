from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    offer_product_ids = fields.One2many(
        'product.offer.line', 'product_tmpl_id', string="Offer Products"
    )
    main_product_ids = fields.One2many(
        'product.main.line', 'product_tmpl_id', string="Main Products"
    )