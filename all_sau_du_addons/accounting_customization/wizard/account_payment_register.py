# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    bank_transaction_number = fields.Char(copy=False)

    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        string="Attachments",
    )
    is_already_attach = fields.Boolean(string="Is Already Attached?")

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals["bank_transaction_number"] = self.bank_transaction_number
        return payment_vals

    def action_create_payments(self):
        # call original method to generate payments
        res = super().action_create_payments()
        if not self.is_already_attach:
            raise ValidationError(_("Please add necessary attachment!"))
        for wizard in self:
            account_env = self.env["account.move"]
            vendor_bill_id = account_env.browse(self._context.get("active_id"))
            for attachment in self.attachment_ids:
                attachment.copy(
                    {
                        "res_model": "account.move",
                        "res_id": vendor_bill_id.id,
                    }
                )
        return res

    @api.onchange("attachment_ids")
    def _onchange_attachment_checkbox(self):
        if self.attachment_ids:
            self.is_already_attach = True
