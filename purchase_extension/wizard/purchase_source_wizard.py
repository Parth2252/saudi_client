# wizard/purchase_source_wizard.py
from odoo import models, fields, api

class PurchaseSourceWizard(models.TransientModel):
    _name = "purchase.source.wizard"
    _description = "Update Purchase Source"

    purchase_source = fields.Selection([
        ('standard', 'Standard Purchase'),
        ('local', 'Local Purchase'),
        ('online', 'Online Purchase'),
    ], string="Purchase Source", required=True)

    def update_purchase_source(self):
        active_ids = self.env.context.get('active_ids', [])
        orders = self.env['purchase.order'].browse(active_ids)
        orders.write({'purchase_source': self.purchase_source})
        return {'type': 'ir.actions.act_window_close'}
