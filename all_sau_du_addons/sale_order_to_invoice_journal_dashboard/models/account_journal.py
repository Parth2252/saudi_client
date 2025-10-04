import json
from odoo import models, fields
from odoo.tools import format_amount


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # count = fields.Float(default=10)

    def _fill_sale_purchase_dashboard_data(self, dashboard_data):
        """Inherit the method to get the value from sale order and display the domain
        fetch data in accounting dashboard.
        We have to add the xml code directly into the addons 'account' module."""

        # <div class="alert alert-info" t-if="journal_type == 'sale'">
        #   <strong>Ready To Invoice: </strong>
        #   <a type="object" name="action_open_sale_orders_to_invoice" context="{'search_default_to_check': True}"><span><t t-esc="dashboard.sale_orders_to_invoice_count"/> Orders</span></a><br/>
        #   <span><strong>Total Amount: </strong><t t-esc="dashboard.sale_orders_to_invoice_total"/></span>
        # </div>

        res = super()._fill_sale_purchase_dashboard_data(dashboard_data)

        # Now add Sale Order "To Invoice" data for sale journals.
        for journal in self:
            sale_orders = self.env["sale.order"].search(
                [
                    ("invoice_status", "=", "to invoice"),
                    ("company_id", "=", journal.company_id.id),
                    ("delivery_status", "=", "full"),
                ]
            )

            sale_orders_count = len(sale_orders)
            sale_orders_total = sum(sale_orders.mapped("amount_total"))
            formatted_total = format_amount(
                self.env, sale_orders_total, journal.company_id.currency_id
            )

            partially_paid_vendor_bills = self.env["account.move"].search(
                [
                    ("status_in_payment", "=", "partial"),
                    ("company_id", "=", journal.company_id.id),
                    ("move_type", "=", "in_invoice"),
                ]
            )
            partially_paid_vendor_bills_count = len(partially_paid_vendor_bills)
            partially_paid_vendor_bills_total = sum(partially_paid_vendor_bills.mapped("amount_total"))
            formatted_partially_paid_vendor_bills_amount = format_amount(
                self.env, partially_paid_vendor_bills_total, journal.company_id.currency_id
            )

            fully_paid_vendor_bills = self.env["account.move"].search(
                [
                    ("status_in_payment", "=", "paid"),
                    ("company_id", "=", journal.company_id.id),
                    ("move_type", "=", "in_invoice"),
                ]
            )
            fully_paid_vendor_bills_count = len(fully_paid_vendor_bills)
            fully_paid_vendor_bills_total = sum(fully_paid_vendor_bills.mapped("amount_total"))
            formatted_fully_paid_vendor_bills_amount = format_amount(
                self.env, fully_paid_vendor_bills_total, journal.company_id.currency_id
            )

            dashboard_data[journal.id].update(
                {
                    "sale_orders_to_invoice_count": sale_orders_count,
                    "sale_orders_to_invoice_total": formatted_total,
                    "partially_paid_vendor_bills_count": partially_paid_vendor_bills_count,
                    "formatted_partially_paid_vendor_bills_amount": formatted_partially_paid_vendor_bills_amount,
                    "fully_paid_vendor_bills_count": fully_paid_vendor_bills_count,
                    "formatted_fully_paid_vendor_bills_amount": formatted_fully_paid_vendor_bills_amount

                }
            )
        return res

    def action_open_sale_orders_to_invoice(self):
        """New method for open sale order view with the domain fetch records."""
        self.ensure_one()
        action = self.env.ref("sale.action_orders").read()[0]
        action.update(
            {
                "domain": [
                    ("invoice_status", "=", "to invoice"),
                    ("company_id", "=", self.company_id.id),
                    ("delivery_status", "=", "full"),
                ],
                "context": {
                    "search_default_filter_to_invoice": 1,
                },
            }
        )
        return action

    def action_open_partially_paid_vendor_bill(self):
        """New method for open sale order view with the domain fetch records."""
        self.ensure_one()
        action = self.env.ref("account.action_move_in_invoice_type").read()[0]
        action.update(
            {
                "domain": [
                    ("status_in_payment", "=", "partial"),
                    ("company_id", "=", self.company_id.id),
                    ("move_type", "=", "in_invoice"),
                ],
                "context": {
                    "search_default_filter_to_invoice": 1,
                },
            }
        )
        return action

    def action_open_fully_paid_vendor_bill(self):
        """New method for open sale order view with the domain fetch records."""
        self.ensure_one()
        action = self.env.ref("account.action_move_in_invoice_type").read()[0]
        action.update(
            {
                "domain": [
                    ("status_in_payment", "=", "paid"),
                    ("company_id", "=", self.company_id.id),
                    ("move_type", "=", "in_invoice"),
                ],
                "context": {
                    "search_default_filter_to_invoice": 1,
                },
            }
        )
        return action

    def action_internal_transfer_1(self):
        """Open Internal Transfer form with current journal pre-filled"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_account_payment_form').id,
            'target': 'current',
            'context': {
                'default_is_internal_transfer': True, 
                'default_journal_id': self.id,
            },
        }