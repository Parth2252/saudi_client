from odoo import models

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, company_id, origins, values):
        """ Method for passing value from sale order to purchase order. """

        res = super()._prepare_purchase_order(company_id=company_id, origins=origins, values=values)
        res['po_reference'] = values[0].get("sale").client_order_ref
        return res
