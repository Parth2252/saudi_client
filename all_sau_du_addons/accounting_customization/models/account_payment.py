from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bank_transaction_number = fields.Char(copy=False)
