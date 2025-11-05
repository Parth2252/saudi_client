# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import fields, models, api


class srAccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    journal_type = fields.Selection(related='journal_id.type')
    bank_charge_amount = fields.Monetary(string="Bank Charges",currency_field="bank_charge_currency_id")
    bank_charge_currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        compute="_compute_bank_charge_currency",
        store=True,
        readonly=True
    )

    @api.depends('journal_type','currency_id')
    def _compute_bank_charge_currency(self):
        sar_currency = self.env['res.currency'].search([
            '|',
            ('name', '=', 'SAR'),
            ('currency_unit_label', '=', 'Riyal'),
        ], limit=1)
        for rec in self:
            rec.bank_charge_currency_id = sar_currency.id if sar_currency else False

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(srAccountPaymentRegister,self)._create_payment_vals_from_wizard(batch_result)
        if payment_vals:
            payment_vals.update({'bank_charge_amount': self.bank_charge_amount, 'bank_charge_currency_id': self.bank_charge_currency_id.id})
        return payment_vals

