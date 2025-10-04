from odoo import models

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_draft(self):
        res = super().action_draft()
        for payment in self:
            bill = self.env['account.move'].search([('name', '=', payment.memo)], limit=1)
            opportunity = bill.opportunity_id
            if bill and bill.opportunity_id and bill.move_type == 'in_invoice':
                confirm_stage = self.env["crm.stage"].search(
                    [("is_vendor_bill_created_state", "=", True)], limit=1
                )
            if bill and bill.opportunity_id and bill.move_type == 'out_invoice':
                confirm_stage = self.env["crm.stage"].search(
                    [("is_customer_invoiced_state", "=", True)], limit=1
                )
            if confirm_stage:
                opportunity.stage_id = confirm_stage.id
        return res
