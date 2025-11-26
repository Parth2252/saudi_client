from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.constrains("product_uom_id")
    def _check_product_uom_category_id(self):
        for line in self:
            if (
                line.product_uom_id
                and line.product_id
                and line.product_uom_id.category_id
                != line.product_id.product_tmpl_id.uom_id.category_id
            ):
                continue
