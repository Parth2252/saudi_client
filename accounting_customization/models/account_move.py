from odoo import models, fields, api, _, Command
from odoo.tools import format_amount

PAYMENT_STATE_SELECTION = [
    ("not_paid", "Not Paid"),
    ("in_payment", "In Payment"),
    ("paid", "Paid"),
    ("partial", "Partially Paid"),
    ("reversed", "Reversed"),
    ("blocked", "Blocked"),
    ("invoicing_legacy", "Invoicing App Legacy"),
]


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_journal_id = fields.Many2one(
        "account.journal",
        string="Payment journal",
        compute="_compute_payment_journal",
        store=True,
    )
    buyer_id = fields.Many2one("res.users", string="Buyer", copy=False)

    # Inherit the field to make store true.
    status_in_payment = fields.Selection(
        selection=PAYMENT_STATE_SELECTION
        + [
            ("draft", "Draft"),
            ("cancel", "Cancelled"),
        ],
        compute="_compute_status_in_payment",
        copy=False,
        store=True,
    )

    @api.depends('state', 'payment_state')
    def _compute_status_in_payment(self):
        for move in self:
            if move.state == 'draft':
                move.status_in_payment = 'draft'
            elif move.state == 'cancel':
                move.status_in_payment = 'cancel'
            else:
                move.status_in_payment = move.payment_state

    sale_partner_id = fields.Many2one('res.partner', string="Sale Customer")
    payment_time_date = fields.Datetime(string="Payment Date")

    @api.depends("matched_payment_ids")
    def _compute_payment_journal(self):
        """New method for set the payment journal in the vendor bill."""
        for move in self:
            payments = move.matched_payment_ids
            if payments:
                move.payment_journal_id = payments[0].journal_id

    def _update_purchase_buyer(self):
        for bill in self:
            if bill.purchase_ids:
                bill.buyer_id = bill.purchase_ids[0].user_id

    def update_sale_customer_from_purchase(self):
        for bill in self:
            if bill.purchase_ids:
                bill.sale_partner_id = bill.purchase_ids[0].sale_partner_id


    @api.depends('line_ids.amount_residual', 'line_ids.date_maturity', 'needed_terms')
    def _compute_invoice_date_due(self):
        today = fields.Date.context_today(self)

        for move in self:

            # -------------------------
            # 1) Installment-based logic
            # -------------------------
            unpaid_lines = move.line_ids.filtered(
                lambda l: l.date_maturity and l.amount_residual not in (0.0, 0, 0.00)
            )
            print("=======================unpaid_lines=====================>",unpaid_lines)
            # IF installments exist → use installment logic
            if move.line_ids.filtered(lambda l: l.date_maturity):

                # CASE 1 → unpaid installments exist
                if unpaid_lines:
                    move.invoice_date_due = min(unpaid_lines.mapped('date_maturity'))
                    continue

                # CASE 2 → all installments fully paid → use last installment date
                all_dates = move.line_ids.filtered(
                    lambda l: l.date_maturity
                ).mapped('date_maturity')

                move.invoice_date_due = max(all_dates) if all_dates else today
                continue

            # -------------------------------------
            # 2) No installments → fallback to needed_terms (Odoo default)
            # -------------------------------------
            if move.needed_terms:
                move.invoice_date_due = max(
                    (k['date_maturity'] for k in move.needed_terms.keys() if k),
                    default=today,
                )
                continue

            # -------------------------------------
            # 3) No terms, no installments → fallback
            # -------------------------------------
            move.invoice_date_due = move.invoice_date_due or today

    @api.model
    def retrieve_dashboard(self):
        """Returns the values to populate the custom dashboard in
        the account move views.
        """
        self.browse().check_access("read")
        today = fields.Date.context_today(self)
        
        move_type = 'in_invoice'
        company_id = self.env.company.id
        currency = self.env.company.currency_id

        # To Validate
        to_validate = self.search([
            ('move_type', '=', move_type),
            ('state', '=', 'draft'),
            ('company_id', '=', company_id)
        ])
        
        # Today Payable
        today_payable = self.search([
            ('move_type', '=', move_type),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('invoice_date_due', '=', today),
            ('company_id', '=', company_id)
        ])

        # Late Payments
        late_payments = self.search([
            ('move_type', '=', move_type),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('invoice_date_due', '<', today),
            ('company_id', '=', company_id)
        ])

        # Partially Paid Bills
        partially_paid = self.search([
            ('move_type', '=', move_type),
            ('status_in_payment', '=', 'partial'),
            ('company_id', '=', company_id)
        ])

        # Fully Paid Bills
        fully_paid = self.search([
            ('move_type', '=', move_type),
            ('status_in_payment', '=', 'paid'),
            ('company_id', '=', company_id)
        ])

        # Credit Note
        credit_note = self.search([
            ('move_type', '=', 'in_refund'),
            ('company_id', '=', company_id)
        ])

        # Utility Bills (Placeholder - logic to be confirmed)
        utility_bills = self.search([
            ('move_type', '=', move_type),
            ('company_id', '=', company_id),
            ('journal_id.name', 'ilike', 'Utility') # Example check
        ])

        def get_data(records, total_field='amount_total'):
            return {
                'count': len(records),
                'total': format_amount(self.env, sum(records.mapped(total_field)), currency)
            }

        result = {
            'to_validate': get_data(to_validate),
            'today_payable': get_data(today_payable, 'amount_residual'),
            'late_payments': get_data(late_payments, 'amount_residual'),
            'partially_paid': get_data(partially_paid, 'amount_residual'),
            'fully_paid': get_data(fully_paid),
            'credit_note': get_data(credit_note),
            'utility_bills': get_data(utility_bills),
        }
        return result



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def action_register_payment(self, ctx=None):
        ''' Open the account.payment.register wizard to pay the selected journal items.
        :return: An action opening the account.payment.register wizard.
        '''
        context = {
            'active_model': 'account.move.line',
            'active_ids': self.ids,
        }
        if ctx:
            context.update(ctx)
        return {
            'name': _('Pay'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }