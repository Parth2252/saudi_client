import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import format_date
from babel.numbers import format_currency
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = "Custom Invoice with Installment and TSV Sequence"

    beneficiary_country = fields.Many2one(related='partner_id.beneficiary_country', string='Beneficiary Country',
                                          readonly=False)
    beneficiary_currency_id = fields.Many2one(related='partner_id.beneficiary_currency_id',
                                              string='Beneficiary Currency', readonly=False)
    account_number = fields.Char(related='partner_id.account_number', string='Account Number', readonly=False)
    iban_number = fields.Char(related='partner_id.iban_number', string='IBAN Number', readonly=False)
    beneficiary_bank_name = fields.Char(related='partner_id.beneficiary_bank_name', string='Bank Name', readonly=False)
    bank_city = fields.Char(related='partner_id.bank_city', string='Bank City', readonly=False)
    swift_code = fields.Char(related='partner_id.swift_code', string='Swift Code', readonly=False)
    beneficiary_full_name = fields.Char(related='partner_id.beneficiary_full_name', string='Full Name', readonly=False)
    beneficiary_short_name = fields.Char(related='partner_id.beneficiary_short_name', string='Short Name',
                                         readonly=False)
    beneficiary_address = fields.Text(related='partner_id.beneficiary_address', string='Address', readonly=False)
    beneficiary_city = fields.Char(related='partner_id.beneficiary_city', string='Beneficiary City', readonly=False)
    postal_code = fields.Char(related='partner_id.postal_code', string='Postal Code', readonly=False)

    purchase_ids = fields.Many2many(
        'purchase.order',
        compute='_compute_purchase_ids',
        string='Purchase Orders',
        store=False
    )

    @api.depends('invoice_line_ids.purchase_line_id.order_id')
    def _compute_purchase_ids(self):
        for move in self:
            pos = move.invoice_line_ids.mapped('purchase_line_id.order_id')
            move.purchase_ids = pos


    amount_due_from_terms = fields.Text(
        string="Installment Schedule",
        compute="_compute_amount_due_from_terms",
        store=False,
    )

    _sequence_field = "name"
    _sequence_date_field = "date"
    _sequence_index = "journal_id"

    # def _get_starting_sequence(self):
    #     return "TSV-BILL-0000-00-0000"

    # def _get_last_sequence_domain(self, relaxed=False):
    #     res = super()._get_last_sequence_domain(relaxed)
    #     if self.date:
    #         self.ensure_one()
    #         year = self.date.year
    #         month = "%02d" % self.date.month
    #         prefix = f"TSV-BILL-{year}-{month}"
    #         return "WHERE name ILIKE %(prefix)s || '%%'", {"prefix": prefix}
    #     return res

    # def _get_sequence_format_param(self, previous):
    #     regex = r'^TSV-BILL-(?P<year>\d{4})-(?P<month>\d{2})-(?P<seq>\d+)$'
    #     match = re.match(regex, previous)
    #     if not match:
    #         raise ValidationError(_('Invalid sequence format: %s') % previous)

    #     values = match.groupdict()
    #     values['year'] = int(values['year'])
    #     values['month'] = int(values['month'])
    #     values['seq'] = int(values['seq'])
    #     values['seq_length'] = len(match.group('seq'))
    #     values['year_length'] = len(match.group('year'))  # ✅ Required
    #     values['year_end'] = values['year']  # ✅ Default fallback
    #     values['year_end_length'] = values['year_length']  # ✅ Required too

    #     format_string = "TSV-BILL-{year}-{month:02d}-{seq:0" + str(values['seq_length']) + "d}"
    #     return format_string, values

    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super().create(vals_list)
    #     for rec in records:
    #         if not rec.name or rec.name == '/':
    #             rec._set_next_sequence()
    #     return records

    # def action_post(self):
    #     for move in self:
    #         if not move.name or move.name == '/':
    #             move._set_next_sequence()
    #         print("==============MOVE NAME=============>",move.name)
    #     return super().action_post()

    # --- Installment logic remains unchanged ---
    def get_installment_schedule(self):
        self.ensure_one()
        currency = self.currency_id or self.company_id.currency_id
        date = self.invoice_date or self.date or fields.Date.context_today(self)
        total = self.amount_total

        if not self.invoice_payment_term_id:
            return [{
                'due_date': date,
                'due_date_str': format_date(self.env, date),
                'amount': currency.round(total),
                'currency': currency,
            }]

        company = self.company_id
        untaxed_total = self.amount_untaxed_signed
        tax_amount = total - untaxed_total

        payment_term_data = self.invoice_payment_term_id._compute_terms(
            date_ref=date,
            currency=currency,
            company=company,
            tax_amount=tax_amount,
            tax_amount_currency=tax_amount,
            untaxed_amount=untaxed_total,
            untaxed_amount_currency=untaxed_total,
            sign=1,
        )   

        result = []
        for line in payment_term_data.get('line_ids', []):
            result.append({
                'due_date': line['date'],
                'due_date_str': format_date(self.env, line['date']),
                'amount': currency.round(line['foreign_amount']),
                'currency': currency,
            })
        return result

    @api.depends('invoice_payment_term_id', 'invoice_date', 'date', 'amount_total', 'currency_id')
    def _compute_amount_due_from_terms(self):
        for move in self:
            try:
                lines = move.get_installment_schedule()
                move.amount_due_from_terms = "\n".join(
                    [
                        f"Installment of {format_currency(l['amount'], l['currency'].name, locale=self.env.context.get('lang', 'en_US'))} due on {l['due_date_str']}"
                        for l in lines]
                )
            except Exception:
                move.amount_due_from_terms = ""

    def action_post(self):
        for record in self:
            if record.move_type in ['in_invoice', 'in_refund']:  # Vendor Bills and Refunds
                partner = record.partner_id
                missing_fields = []

                # Map of partner fields to human-readable names
                required_fields = {
                    'beneficiary_country': 'Beneficiary Country',
                    'beneficiary_currency_id': 'Beneficiary Currency',
                    'account_number': 'Account Number',
                    'iban_number': 'IBAN Number',
                    'beneficiary_bank_name': 'Bank Name',
                    'bank_city': 'Bank City',
                    'swift_code': 'Swift Code',
                    'beneficiary_full_name': 'Full Name',
                    'beneficiary_short_name': 'Short Name',
                    'beneficiary_address': 'Address',
                    'beneficiary_city': 'Beneficiary City',
                    'postal_code': 'Postal Code',
                }

                for field, label in required_fields.items():
                    if not getattr(partner, field):
                        missing_fields.append(label)

                if missing_fields:
                    raise ValidationError(
                        "You cannot confirm this vendor bill because the following fields "
                        "are missing on the partner:\n- %s" % "\n- ".join(missing_fields)
                    )
            if record.name == '/':
                if record.move_type == 'out_invoice':
                    record.name = self.env['ir.sequence'].with_context(
                        ir_sequence_date=record.date).next_by_code('tsv.invoice.sequence') or '/'
                elif record.move_type == 'in_invoice':
                    record.name = self.env['ir.sequence'].with_context(
                        ir_sequence_date=record .date).next_by_code('tsv.bill.sequence') or '/'
        return super().action_post()
