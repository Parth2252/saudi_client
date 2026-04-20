from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    purchase_source = fields.Selection(
        [
            ("standard", "Standard Purchase"),
            ("local", "Local Purchase"),
            ("online", "Online Purchase"),
        ],
        string="Purchase Source",
    )
    sale_partner_id = fields.Many2one('res.partner', string='Sale Customer')
    po_status = fields.Selection(
        related="purchase_id.po_status", string="PO Status", store=True
    )
    billing_status = fields.Selection(
        related="purchase_id.invoice_status", string="Billing Status", store=True
    )
    extra_qty_reason = fields.Text(string='Extra Qty Reason', readonly=True)
    show_qty_warning = fields.Boolean(compute="_compute_show_qty_warning")

    @api.depends('move_ids.quantity')
    def _compute_show_qty_warning(self):
        for rec in self:
            # Show warning if any incoming move linked to a PO has 0 quantity
            rec.show_qty_warning = rec.picking_type_code == 'incoming' and any(
                m.purchase_line_id and m.quantity == 0 for m in rec.move_ids
            )

    def action_confirm(self):
        res = super().action_confirm()
        for picking in self:
            if picking.picking_type_code == 'incoming' and picking.purchase_id:
                picking.move_ids.write({'quantity': 0.0})
                picking.move_line_ids.write({'quantity': 0.0})
        return res

    def button_validate(self):
        for picking in self:
            if picking.picking_type_code == 'incoming' and not picking.extra_qty_reason:
                over_qty_lines = []
                po_lines_in_picking = {}
                for move in picking.move_ids.filtered(lambda m: m.purchase_line_id and m.quantity > 0):
                    if move.purchase_line_id not in po_lines_in_picking:
                        po_lines_in_picking[move.purchase_line_id] = {
                            'qty': 0.0,
                            'product_name': move.product_id.display_name
                        }
                    po_lines_in_picking[move.purchase_line_id]['qty'] += move.quantity

                for po_line, data in po_lines_in_picking.items():
                    total_receipt_qty = po_line.qty_received + data['qty']
                    if total_receipt_qty > po_line.product_qty:
                        extra_qty = total_receipt_qty - po_line.product_qty
                        over_qty_lines.append({
                            'po_qty': po_line.product_qty,
                            'total_receipt_qty': total_receipt_qty,
                            'extra_qty': extra_qty,
                            'product_name': data['product_name']
                        })

                if over_qty_lines:
                    if not self.env.user.has_group('purchase_extension.group_allow_receipt_extra_qty'):
                        msg = "You are receiving more than the purchased quantity!\n\n"
                        for line in over_qty_lines:
                            msg += f"Product: {line['product_name']}\nPurchase Qty: {line['po_qty']}\nTotal Receiving: {line['total_receipt_qty']}\nExtra Qty: {line['extra_qty']}\n\nYou do not have the rights to process extra quantity."
                        from odoo.exceptions import UserError
                        raise UserError(msg)
                    else:
                        ctx = dict(self.env.context, default_picking_id=picking.id)
                        return {
                            'name': _('Extra Quantity Reason'),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'receipt.extra.qty.wizard',
                            'target': 'new',
                            'context': ctx,
                        }

        return super().button_validate()
