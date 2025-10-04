# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    opportunity_id = fields.Many2one("crm.lead", string="Opportunity", copy=False)


    @api.constrains('state')
    def check_move_state(self):
        for record in self:
            if not record.opportunity_id:
                continue

            # ================= Vendor Bill (in_invoice) =================
            if record.move_type == 'in_invoice':
                # All POs linked to this opportunity
                all_pos = self.env["purchase.order"].search([
                    ("opportunity_id", "=", record.opportunity_id.id)
                ])

                if all_pos:
                    all_bills = self.env["account.move"].search([
                        ("purchase_ids", "in", all_pos.ids),
                        ("move_type", "=", "in_invoice"),
                        ("opportunity_id", "=", record.opportunity_id.id),
                    ])

                    all_po_billed = True
                    for po in all_pos:
                        po_bills = all_bills.filtered(lambda b: po.id in b.purchase_ids.ids)
                        if not po_bills or not all(bill.state == "posted" for bill in po_bills):
                            all_po_billed = False
                            break

                    if all_po_billed:
                        vendor_bill_created_state = self.env["crm.stage"].search(
                            [("is_vendor_bill_created_state", "=", True)], limit=1
                        )
                        if vendor_bill_created_state:
                            record.opportunity_id.stage_id = vendor_bill_created_state.id
                    else:
                        vendor_bill_cancel_state = self.env["crm.stage"].search(
                            [("is_po_confirm_state", "=", True)], limit=1
                        )
                        if vendor_bill_cancel_state:
                            record.opportunity_id.stage_id = vendor_bill_cancel_state.id
                            

            # ================= Customer Invoice (out_invoice) =================
            if record.move_type == 'out_invoice':
                # All SOs linked to this opportunity
                all_sos = self.env["sale.order"].search([
                    ("opportunity_id", "=", record.opportunity_id.id)
                ])

                if all_sos:
                    all_invoices = self.env["account.move"].search([
                        ("invoice_origin", "in", all_sos.mapped("name")),
                        ("move_type", "=", "out_invoice"),
                        ("opportunity_id", "=", record.opportunity_id.id),
                    ])

                    all_so_invoiced = True
                    for so in all_sos:
                        so_invoices = all_invoices.filtered(lambda inv: inv.invoice_origin == so.name)
                        if not so_invoices or not all(inv.state == "posted" for inv in so_invoices):
                            all_so_invoiced = False
                            break

                    if all_so_invoiced:
                        customer_invoice_created_state = self.env["crm.stage"].search(
                            [("is_customer_invoiced_state", "=", True)], limit=1
                        )
                        if customer_invoice_created_state:
                            record.opportunity_id.stage_id = customer_invoice_created_state.id
                    else:
                        customer_invoice_cancel_state = self.env["crm.stage"].search(
                            [("is_grn_entered_state", "=", True)], limit=1
                        )
                        if customer_invoice_cancel_state:
                            record.opportunity_id.stage_id = customer_invoice_cancel_state.id