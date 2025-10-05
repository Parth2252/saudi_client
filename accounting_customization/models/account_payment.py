from odoo import fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bank_transaction_number = fields.Char(copy=False)

    is_already_attach = fields.Boolean(string="Is Already Attached?")

    def action_post(self):
        res = super().action_post()

        # Skip validation if coming from the payment register wizard
        if self.env.context.get('active_model') == 'account.move':
            return res

        for payment in self:
            if self._context.get('internal_transfer') and not payment.is_already_attach:
                raise ValidationError(
                    "Please add an attachment. If you have already attached the document, "
                    "please enable the checkbox 'Is Already Attached?'."
                )
            return res

