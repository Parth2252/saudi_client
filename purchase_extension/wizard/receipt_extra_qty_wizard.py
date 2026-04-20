from odoo import models, fields, api, _

class ReceiptExtraQtyWizard(models.TransientModel):
    _name = 'receipt.extra.qty.wizard'
    _description = 'Receipt Extra Quantity Wizard'

    picking_id = fields.Many2one('stock.picking', string='Receipt')
    reason = fields.Text('Reason for Extra Quantity', required=True)

    def action_confirm(self):
        self.ensure_one()
        self.picking_id.extra_qty_reason = self.reason
        return self.picking_id.button_validate()
