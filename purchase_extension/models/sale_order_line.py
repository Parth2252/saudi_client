from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id", "offered_description_id")
    def onchange_product_uom(self):
        if self.offered_description_id:
            self.product_uom = self.offered_description_id.uom_id.id
        else:
            self.product_uom = self.product_id.uom_id.id
