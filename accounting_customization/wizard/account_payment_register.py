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
        # 1) call original method (it returns an action dict or True)
        res = super().action_create_payments()

        # optional: debug what we got back (useful while testing)
        _logger.info("action_create_payments returned: %s", res)

        if not self.is_already_attach:
            raise ValidationError(_("Please add necessary attachment!"))

        # 2) try to extract created payments from the returned action
        payments = self.env['account.payment']
        try:
            if isinstance(res, dict):
                # single payment returned as res_id
                if res.get('res_id'):
                    payments = self.env['account.payment'].browse(res['res_id'])
                # or multiple payments returned in domain e.g. domain: [('id','in',[...])]
                elif res.get('domain'):
                    domain = res.get('domain')
                    # find ("id", "in", [..]) tuple
                    for d in domain:
                        if isinstance(d, (list, tuple)) and len(d) >= 3 and d[0] == 'id' and d[1] == 'in':
                            payments = self.env['account.payment'].browse(d[2])
                            break
        except Exception as e:
            _logger.exception("Couldn't parse payments from action: %s", e)

        # 3) get invoices that were actually reconciled by those payments
        invoices = self.env['account.move']
        if payments:
            # prefer reconciled_invoice_ids (newer Odoo)
            invoices = payments.mapped('reconciled_invoice_ids') or payments.mapped('invoice_ids')
            _logger.info("Found invoices from payments: %s", invoices.ids)
        # 4) fallback: maybe wizard was called with active_model/account.move context
        if not invoices:
            active_model = self._context.get('active_model')
            if active_model == 'account.move':
                active_ids = self._context.get('active_ids') or ([self._context.get('active_id')] if self._context.get('active_id') else [])
                invoices = self.env['account.move'].browse(active_ids)
                _logger.info("Fallback to invoices from context.active_ids: %s", invoices.ids)

        # 5) last resort: if still nothing, log and return
        if not invoices:
            _logger.warning("No invoices found to attach files to. context=%s, res=%s", self._context, res)
            return res

        # 6) copy attachments to each invoice, avoid duplicates
        Attachment = self.env['ir.attachment']
        for wizard in self:
            for attachment in wizard.attachment_ids:
                for inv in invoices:
                    # avoid exact duplicate (same filename + owner + model/record)
                    found = Attachment.search([
                        ('res_model', '=', 'account.move'),
                        ('res_id', '=', inv.id),
                        ('name', '=', attachment.name),
                        ('datas', '=', attachment.datas),
                    ], limit=1)
                    if not found:
                        attachment.copy({
                            'res_model': 'account.move',
                            'res_id': inv.id,
                        })
                        _logger.info("Copied attachment %s to invoice %s", attachment.name, inv.id)
                    else:
                        _logger.info("Attachment %s already present on invoice %s - skipping", attachment.name, inv.id)

        return res

    @api.onchange("attachment_ids")
    def _onchange_attachment_checkbox(self):
        if self.attachment_ids:
            self.is_already_attach = True
