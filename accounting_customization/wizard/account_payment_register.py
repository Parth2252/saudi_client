# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

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
        # 1) call original method
        res = super().action_create_payments()

        if not self.is_already_attach:
            raise ValidationError(_("Please add necessary attachment!"))

        account_move_env = self.env["account.move"]
        Attachment = self.env["ir.attachment"]

        # 2) extract created payments (for multiple bills)
        payments = self.env["account.payment"]
        if isinstance(res, dict):
            if res.get("res_id"):
                payments = self.env["account.payment"].browse(res["res_id"])
            elif res.get("domain"):
                for dom in res["domain"]:
                    if (
                        isinstance(dom, (list, tuple))
                        and len(dom) >= 3
                        and dom[0] == "id"
                        and dom[1] == "in"
                    ):
                        payments = self.env["account.payment"].browse(dom[2])
                        break

        # 3) determine related invoices
        invoices = self.env["account.move"]
        if payments:
            invoices = payments.mapped("reconciled_invoice_ids") or payments.mapped("invoice_ids")

        # 4) fallback logic (your original one)
        if not invoices:
            active_id = self._context.get("active_id")
            if active_id:
                invoices = account_move_env.browse(active_id)
            else:
                active_ids = self._context.get("active_ids") or []
                if active_ids:
                    invoices = account_move_env.browse(active_ids)

        if not invoices:
            _logger.warning("No invoices found to attach files to. context=%s", self._context)
            return res

        # 5) copy attachments
        for wizard in self:
            for attachment in wizard.attachment_ids:
                for inv in invoices:
                    # skip duplicates (optional)
                    found = Attachment.search([
                        ("res_model", "=", "account.move"),
                        ("res_id", "=", inv.id),
                        ("name", "=", attachment.name),
                        ("datas", "=", attachment.datas),
                    ], limit=1)
                    if not found:
                        attachment.copy({
                            "res_model": "account.move",
                            "res_id": inv.id,
                        })
                        _logger.info("Attachment %s copied to invoice %s", attachment.name, inv.name)

        return res

    @api.onchange("attachment_ids")
    def _onchange_attachment_checkbox(self):
        if self.attachment_ids:
            self.is_already_attach = True
