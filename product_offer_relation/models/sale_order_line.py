from odoo import models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_template_id')
    def onchange_product_template(self):
        for rec in self:
            if rec.product_template_id and rec.product_template_id.offer_product_ids:
                offer_product_id =  rec.product_template_id.offer_product_ids[0].product_id.id
                rec.offered_description_id = offer_product_id
