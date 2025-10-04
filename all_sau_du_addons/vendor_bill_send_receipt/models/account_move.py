from odoo import models
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_payment_receipt(self):
        self.ensure_one()
        if self.payment_state != 'paid':
            raise UserError("This bill is not fully paid yet.")

        payments = self._get_reconciled_payments()
        if not payments:
            raise UserError("No related payments found.")

        payment = payments[0]

        template = self.env.ref('account.mail_template_data_payment_receipt', raise_if_not_found=False)
        if not template:
            raise UserError("Payment receipt email template not found.")

        compose_form = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=True)

        ctx = {
            'default_model': 'account.payment',
            'default_res_ids': [payment.id],
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True,
        }

        return {
            'name': 'Send Payment Receipt',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def _get_reconciled_payments(self):
        self.ensure_one()
        payments = self.env['account.payment'].search([
            ('move_id.line_ids.reconciled', '=', True),
            ('move_id.line_ids.account_id', 'in', self.line_ids.mapped('account_id').ids),
            ('partner_id', '=', self.partner_id.id),
        ])
        return payments
