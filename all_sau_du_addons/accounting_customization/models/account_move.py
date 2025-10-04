from odoo import models, fields, api

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

    sale_partner_id = fields.Many2one('res.partner', string="Sale Customer")

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
