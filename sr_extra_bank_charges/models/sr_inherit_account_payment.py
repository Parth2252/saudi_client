        # -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError


class srAccountPayment(models.Model):
    _inherit = "account.payment"

    bank_charge_amount = fields.Monetary('Bank Charges')
    bank_charge_currency_id = fields.Many2one("res.currency", string="Bank Charge Currency")
    bank_charge_move_id = fields.Many2one("account.move", string="Bank Charge Journal Entry", readonly=True)

    # def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
    #     line_vals_list = super(srAccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals, force_balance=force_balance)
    #     if line_vals_list:
    #         if  self.bank_charge_amount > 0.0:
    #             if not self.journal_id.default_bank_charge_account_id:
    #                 raise UserError('Please first configure Bank Charge Account from Invoicing Configuration -> Journals -> Bank(Extra Bank Charge Account)')
    #             for line in line_vals_list:
    #                 if line.get('debit') == 0.0:
    #                     amount_currency = line.get('amount_currency') + (-self.bank_charge_amount)
    #                     credit = line.get('credit') + self.bank_charge_amount
    #                     line.update({'credit': credit, 'amount_currency': amount_currency})
                
    #             line_vals_list.append(
    #             {
    #                 'name': "Bank Charges Payments",
    #                 'date_maturity': self.date,
    #                 'amount_currency': self.bank_charge_amount or 0.0 or 0.0,
    #                 'currency_id': self.bank_charge_currency_id.id,
    #                 'debit': self.bank_charge_amount or 0.0 or 0.0,
    #                 'credit': 0.0,
    #                 'partner_id': self.partner_id.id,
    #                 'account_id': self.journal_id.default_bank_charge_account_id.id,
    #             }
    #             )
    #     return line_vals_list

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)
        for pay in payments:
            if pay.bank_charge_amount > 0:
                pay._generate_bank_charge_move()
        return payments

    def _generate_bank_charge_move(self, write_off_line_vals=None, force_balance=None, line_ids=None):
        """Generate a separate journal entry for bank charges and link it to the payment"""
        for payment in self:
            # Skip if no bank charge
            if not payment.bank_charge_amount or payment.bank_charge_amount == 0.0:
                continue
            journal_id = self.env['account.journal'].sudo().search([('is_bank_charges', '=', True)],limit=1)
            # Ensure bank charge account is configured
            if not journal_id.default_bank_charge_account_id:
                raise UserError(
                    "Please configure Bank Charge Account in Journals (Invoicing Configuration -> Journals -> Bank)."
                )

            # Prepare move lines
            move_lines = [
                Command.create({
                    'account_id': journal_id.default_bank_charge_account_id.id,
                    'name': 'Bank Charge',
                    'debit': payment.bank_charge_amount,
                    'credit': 0.0,
                    'currency_id': payment.bank_charge_currency_id.id or payment.currency_id.id,
                    'amount_currency': payment.bank_charge_amount,
                    # 'partner_id': payment.partner_id.id,
                }),
                Command.create({
                    'account_id': (
                        journal_id.default_account_id.id
                    ),
                    'name': 'Bank Charge (Bank Side)',
                    'debit': 0.0,
                    'credit': payment.bank_charge_amount,
                    'currency_id': payment.bank_charge_currency_id.id or payment.currency_id.id,
                    'amount_currency': -payment.bank_charge_amount,
                    # 'partner_id': payment.partner_id.id,
                }),
            ]

            # Prepare move values
            move_vals = {
                'move_type': 'entry',
                'ref': f"{payment.memo or ''} - Bank Charge",
                'date': payment.date,
                'journal_id': journal_id.id,
                'company_id': payment.company_id.id,
                # 'partner_id': payment.partner_id.id,
                'currency_id': payment.bank_charge_currency_id.id or payment.currency_id.id,
                'origin_payment_id': payment.id,
                'line_ids': move_lines,
            }

            # Create and post move
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            # Link move with payment
            payment.bank_charge_move_id = move.id

        return True


    def button_open_journal_entry(self):
        """Open both payment and bank charge journal entries in a list view."""
        self.ensure_one()
        moves = self.env['account.move'].browse(
            filter(None, [self.move_id.id, self.bank_charge_move_id.id])
        )
        return {
            'name': _("Journal Entries"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', moves.ids)],
            'context': {'create': False},
        }
