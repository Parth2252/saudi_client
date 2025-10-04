# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _

class SaleAdvancePayment(models.TransientModel):
    _name = 'sale.advance.payment'
    _description = 'Sale Advance Payment'

    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True,
                                 domain=[('type', 'in', ['cash', 'bank'])])
    pay_amount = fields.Float(string="Payable Amount", required=True)
    date_planned = fields.Datetime(string="Advance Payment Date", index=True, default=fields.Datetime.now,
                                   required=True)
    remaining_amount = fields.Float(string="Remaining Amount",readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(SaleAdvancePayment, self).default_get(fields)
        total_advance_payment = 0
        sale_active_id = self.env.context.get('active_id')
        current_sale_order = self.env['sale.order'].browse(sale_active_id)
        if current_sale_order.account_payment_ids:
            for rec in current_sale_order.account_payment_ids:
                total_advance_payment += rec.amount_company_currency_signed
            remain_amount = current_sale_order.amount_total - total_advance_payment
            res.update({'total_amount': remain_amount})
        else:
            res.update({'total_amount': current_sale_order.amount_total})
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
        sale_ids = self.env.context.get('active_ids', [])
        if sale_ids:
            payment_res = self.get_payment(sale_ids)
            payment = payment_obj.create(payment_res)
            payment.update({"payment_info": "Advance Payment Of" + "  " + payment.sale_id.name or False})
            payment.action_post()
            if payment.state != 'paid':
                payment.action_validate()

        return {
            'type': 'ir.actions.act_window_close',
        }

    def get_payment(self, sale_ids):
        sale_obj = self.env['sale.order']
        sale_id = sale_ids[0]
        sale = sale_obj.browse(sale_id)
        payment_res = {
            'payment_type': 'inbound',
            'partner_id': sale.partner_id.id,
            'partner_type': 'customer',
            'journal_id': self[0].journal_id.id,
            'company_id': sale.company_id.id,
            'currency_id': sale.currency_id.id,
            'date': self[0].date_planned,
            'amount': self[0].pay_amount,
            'sale_id': sale.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id
        }
        return payment_res
