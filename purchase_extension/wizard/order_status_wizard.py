from odoo import models, fields, api

class OrderStatusWizard(models.TransientModel):
    _name = 'order.status.wizard'
    _description = 'Order Status Wizard'

    order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    order_status = fields.Selection([
        ("acknowledged", "Order Acknowledged by vendor"),
        ("shipped", "order shipped"),
    ], string="Order Status", required=True)
    tracking_number = fields.Char(string="Tracking Number")

    def action_confirm(self):
        self.ensure_one()
        self.order_id.write({
            'order_status': self.order_status,
            'tracking_number': self.tracking_number,
        })
        return {'type': 'ir.actions.act_window_close'}
