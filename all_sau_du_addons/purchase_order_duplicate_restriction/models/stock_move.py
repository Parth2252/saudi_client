from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        val = super(StockMove, self)._prepare_procurement_values()
        val["sale"] = self.group_id.sale_id
        return val
