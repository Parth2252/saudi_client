# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _

class AdvancePayment(models.TransientModel):
    _name = 'purchase.advance.payment'
    _description = 'Purchase Advance Payment'

    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True,
                                 domain=[('type', 'in', ['cash', 'bank'])])
    pay_amount = fields.Float(string="Payable Amount", required=True)
    date_planned = fields.Datetime(string="Advance Payment Date", index=True, default=fields.Datetime.now,
                                   required=True)
    remaining_amount = fields.Float(string="Remaining Amount",readonly=True)
    
    @api.model
    def default_get(self, fields):
        res = super(AdvancePayment, self).default_get(fields)
        total_advance_payment = 0
        purchase_active_id = self.env.context.get('active_id')
        current_purchase_order = self.env['purchase.order'].browse(purchase_active_id)
        if current_purchase_order.account_payment_ids:
            for rec in current_purchase_order.account_payment_ids:
                total_advance_payment += rec.amount_company_currency_signed
            remain_amount = current_purchase_order.amount_total - (-total_advance_payment)
            res.update({'total_amount': remain_amount})
        else:
            res.update({'total_amount': current_purchase_order.amount_total})
        return res
    
    total_amount = fields.Float(string="Total Amount",readonly=True)

    @api.constrains('pay_amount')
    def check_amount(self):
        if self.pay_amount <= 0:
            raise ValidationError(_("Please Enter Postive Amount"))
        elif self.pay_amount > self.total_amount:
            raise ValidationError(_("Payable Amount is not greater than Total Amount."))
    
    @api.onchange('pay_amount')
    def _onchange_pay_amount(self):
        if self.pay_amount:
            self.remaining_amount = self.total_amount - self.pay_amount

    def make_payment(self):
        payment_obj = self.env['account.payment']
        purchase_ids = self.env.context.get('active_ids', [])
        if purchase_ids:
            payment_res = self.get_payment(purchase_ids)
            payment = payment_obj.create(payment_res)
            payment.update({"payment_info": "Advance Payment Of" + "  " + payment.purchase_id.name or False})
            payment.action_post()
            if payment.state != 'paid':
                payment.action_validate()
        return {
            'type': 'ir.actions.act_window_close',
        }

    def get_payment(self, purchase_ids):
        purchase_obj = self.env['purchase.order']
        purchase_id = purchase_ids[0]
        purchase = purchase_obj.browse(purchase_id)
        payment_res = {
            'payment_type': 'outbound',
            'partner_id': purchase.partner_id.id,
            'partner_type': 'supplier',
            'journal_id': self.journal_id.id,
            'company_id': purchase.company_id.id,
            'currency_id': purchase.currency_id.id,
            'date': self.date_planned,
            'amount': self.pay_amount,
            'purchase_id': purchase.id,
            # 'name': "Advance Payment" + " - " + purchase.name,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id
        }
        return payment_res
