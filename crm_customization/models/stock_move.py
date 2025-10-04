# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = "stock.move"


    def _get_new_picking_values(self):
        """ Method for passing value from sale order to stock move or picking. """
        vals = super(StockMove, self)._get_new_picking_values()
        so = self.sale_line_id.order_id
        vals["opportunity_id"] = so.opportunity_id.id
        return vals