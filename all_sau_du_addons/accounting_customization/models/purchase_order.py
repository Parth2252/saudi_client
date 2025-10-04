from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Purchase(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice(self):
        print("\n\n\n --- prepare invoice ---")
        res = super()._prepare_invoice()
        res['buyer_id'] = self.user_id.id if self.user_id else False
        res['sale_partner_id'] = self.sale_partner_id.id
        return res
