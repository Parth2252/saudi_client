from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    delivery_note_number = fields.Char(
        string="Delivery Note Number",
        compute="_compute_delivery_note_number",
        store=False,
    )
    po_ref = fields.Char(string="PO Reference")

    @api.constrains("po_ref")
    def _check_po_ref_customer_invoice(self):
        for move in self:
            # Apply only for customer invoices being posted (not drafts, not bills)
            if move.move_type == "out_invoice" and not move.po_ref:
                raise ValidationError(
                    "PO Reference is required to confirm a customer invoice."
                )

    def _compute_delivery_note_number(self):
        for move in self:
            # Safely find related pickings through sale order or purchase order
            picking = False
            if move.invoice_origin:
                picking = self.env["stock.picking"].search(
                    [("origin", "=", move.invoice_origin)], limit=1
                )
            move.delivery_note_number = picking.name if picking else ""
