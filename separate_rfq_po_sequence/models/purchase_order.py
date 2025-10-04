from odoo import models, api
import re

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        if vals.get('state', 'draft') == 'draft' and not vals.get('name'):
            seq = self.env['ir.sequence'].next_by_code('purchase.order.rfq') or '/'
            # Replace 4-digit year with last 2 digits
            seq = re.sub(r'(\d{4})(-)', lambda m: m.group(1)[-2:] + m.group(2), seq, 1)
            vals['name'] = seq
        return super(PurchaseOrder, self).create(vals)

    def button_confirm(self):
        for order in self:
            if order.name and order.name.startswith('TS-RFQ-'):
                seq = self.env['ir.sequence'].next_by_code('purchase.order.po') or '/'
                seq = re.sub(r'(\d{4})(-)', lambda m: m.group(1)[-2:] + m.group(2), seq, 1)
                order.name = seq
        return super(PurchaseOrder, self).button_confirm()
