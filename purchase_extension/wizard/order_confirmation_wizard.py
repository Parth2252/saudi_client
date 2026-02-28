from odoo import models, fields, api

class OrderConfirmationWizard(models.TransientModel):
    _name = 'order.confirmation.wizard'
    _description = 'Order Confirmation Wizard'

    order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    confirmation_number = fields.Char(string='Order Confirmation Number', required=True)

    def action_confirm(self):
        self.ensure_one()
        self.order_id.order_confirmation_number = self.confirmation_number
        return {'type': 'ir.actions.act_window_close'}
