# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'


    def action_create_payments(self):
        res = super().action_create_payments()
        account_env = self.env["account.move"]
        account_move_id = account_env.browse(self._context.get("active_id"))

        # ========== Vendor Bill Payment ==========
        if account_move_id.move_type == "in_invoice" and account_move_id.opportunity_id:
            purchase_order = account_move_id.purchase_ids[:1]
            all_vendor_bills = account_env.search([
                ("purchase_ids", "=", purchase_order.id),
                ("move_type", "=", "in_invoice"),
                ("opportunity_id", "=", account_move_id.opportunity_id.id),
                ("id", "!=", account_move_id.id),
            ])
            all_paid = all(bill.payment_state == "paid" for bill in all_vendor_bills)

            if all_paid:
                vendor_bill_paid_state = self.env["crm.stage"].search(
                    [("is_vendor_bill_paid_state", "=", True)], limit=1
                )
                if vendor_bill_paid_state:
                    purchase_order.opportunity_id.stage_id = vendor_bill_paid_state.id

        # ========== Customer Invoice Payment ==========
        if account_move_id.move_type == "out_invoice" and account_move_id.opportunity_id:
            all_customer_invoices = account_env.search([
                ("move_type", "=", "out_invoice"),
                ("opportunity_id", "=", account_move_id.opportunity_id.id),
                ("id", "!=", account_move_id.id),
            ])
            all_paid = all(inv.payment_state == "paid" for inv in all_customer_invoices)

            if all_paid:
                customer_invoice_paid_state = self.env["crm.stage"].search(
                    [("is_customer_invoice_paid_state", "=", True)], limit=1
                )
                if customer_invoice_paid_state:
                    account_move_id.opportunity_id.stage_id = customer_invoice_paid_state.id
        return res
