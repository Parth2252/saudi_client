from odoo import models, _
from odoo.exceptions import UserError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_merge_vendor_bills(self):
        bills = self.env['account.move'].browse(self.env.context.get('active_ids', []))

        if not bills or len(bills) < 2:
            raise UserError(_("Select at least two vendor bills."))

        if any(bill.move_type != 'in_invoice' for bill in bills):
            raise UserError(_("Only vendor bills can be merged."))

        if any(bill.state != 'draft' for bill in bills):
            raise UserError(_("All vendor bills must be in draft state."))

        partner = bills[0].partner_id
        if any(bill.partner_id != partner for bill in bills):
            raise UserError(_("All selected bills must belong to the same vendor."))

        # Pick the first bill as the primary
        primary_bill = bills[0]
        other_bills = bills[1:]

        # Compute the earliest date among all bills
        earliest_invoice_date = min(bills.mapped('invoice_date'))
        earliest_date = min(bills.mapped('date'))
        earliest_invoice_date_due = min(bills.mapped('invoice_date_due'))

        # Collect all non-empty references
        all_refs = [bill.ref for bill in bills if bill.ref]
        combined_ref = ', '.join(dict.fromkeys(all_refs))  # remove duplicates and preserve order

        for bill in other_bills:
            # Copy invoice lines
            for line in bill.invoice_line_ids:
                line.copy({'move_id': primary_bill.id})

            # Move attachments (ir.attachment)
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', bill.id)
            ])
            for att in attachments:
                att.copy({'res_id': primary_bill.id})

            # Cancel the merged bill (you can also unlink if needed)
            bill.button_cancel()
            # bill.unlink()  # Uncomment if you want to delete the bill

        # Update the main bill with earliest date and merged references
        primary_bill.write({
            'invoice_date': earliest_invoice_date,
            'date': earliest_date,
            'invoice_date_due': earliest_invoice_date_due,
            'ref': combined_ref or primary_bill.ref,
        })

        # Recompute
        primary_bill._compute_amount()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Merged Vendor Bill'),
            'res_model': 'account.move',
            'res_id': primary_bill.id,
            'view_mode': 'form',
            'target': 'current',
        }
