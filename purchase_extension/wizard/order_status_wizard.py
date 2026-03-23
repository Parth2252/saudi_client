from odoo import models, fields, api

class OrderStatusWizard(models.TransientModel):
    _name = 'order.status.wizard'
    _description = 'Order Status Wizard'

    order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    order_status = fields.Selection([
        ("acknowledged", "Order Acknowledged by Vendor"),
        ("shipped", "Order Shipped"),
    ], string="Order Status", required=True)
    tracking_number = fields.Char(string="Tracking Number")

    def action_confirm(self):
        self.ensure_one()
        if self.order_status == 'acknowledged':
            is_paid = any(inv.payment_state in ('paid', 'in_payment') for inv in self.order_id.invoice_ids)
            if not self.order_id.invoice_ids or not is_paid:
                from odoo.exceptions import ValidationError
                raise ValidationError("You can only set the order status to 'Acknowledged' when a bill is created and fully paid.")
        self.order_id.write({
            'order_status': self.order_status,
            'tracking_number': self.tracking_number,
        })
        return {'type': 'ir.actions.act_window_close'}
