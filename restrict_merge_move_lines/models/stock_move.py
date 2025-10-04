from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    def _merge_moves(self, merge_into=False):
        return self
