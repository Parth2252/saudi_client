from odoo import models
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_payment_receipt(self):
        self.ensure_one()
        payments = self._get_reconciled_payments()
        if not payments:
            raise UserError("No posted payment found for this bill.")
        payment = payments[0]
        return self.env.ref('account.action_report_payment_receipt').report_action(payment)
