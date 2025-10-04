from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_creation_date = fields.Datetime(
        string="Payment Date",
        default=False,
        compute="_compute_payment_date",
        store=True,
    )

    @api.depends("matched_payment_ids")
    def _compute_payment_date(self):
        """New method for set the payment creation date in the vendor bill."""
        for move in self:
            payments = move.matched_payment_ids
            print("\n\n\n --- paymentes ----", payments)
            move.payment_creation_date = payments[0].create_date if payments else False
