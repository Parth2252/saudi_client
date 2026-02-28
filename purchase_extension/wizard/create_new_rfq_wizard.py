from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError

class CreateNewRFQWizard(models.TransientModel):
    _name = 'create.new.rfq.wizard'
    _description = 'Create New RFQ from Selected Lines'

    purchase_id = fields.Many2one('purchase.order', string='Original RFQ', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    warning_message = fields.Text(string="Warning", readonly=True, default="Note: All details (except Vendor) and selected lines will be copied from the current RFQ. Selected lines will be removed from the original RFQ.")

    @api.model
    def default_get(self, fields):
        res = super(CreateNewRFQWizard, self).default_get(fields)
        if self._context.get('active_id'):
            purchase = self.env['purchase.order'].browse(self._context.get('active_id'))
            res.update({
                'purchase_id': purchase.id,
                'partner_id': purchase.partner_id.id,
            })
        return res

    def action_create_rfq(self):
        self.ensure_one()
        original_po = self.purchase_id
        selected_lines = original_po.order_line.filtered(lambda l: l.select_for_new_rfq and not l.display_type)

        if not selected_lines:
            raise UserError(_("Please select at least one line to create a new RFQ."))

        # Prepare line values using Command pattern
        new_lines_vals = []
        for line in selected_lines:
            line_vals = line.copy_data({
                'select_for_new_rfq': False,
                'customer_pdd': line.customer_pdd,  # copy=False in model, so must pass explicitly
                'sale_line_id': line.sale_line_id.id, # preserve link to Sale Order
            })[0]
            new_lines_vals.append(Command.create(line_vals))

        # Prepare PO values
        # We use copy_data to get all standard fields and then override/add our custom fields
        po_vals = original_po.copy_data({
            'partner_id': self.partner_id.id,
            'order_line': new_lines_vals,
            'state': 'draft',
            'origin': original_po.name,
            'date_planned': original_po.date_planned,
            'po_expire_date': original_po.po_expire_date,
            'print_vendor_item_code_and_name': original_po.print_vendor_item_code_and_name,
            'customer_contact_id': original_po.customer_contact_id.id,
            'partner_invoice_id': original_po.partner_invoice_id.id,
            'partner_shipping_id': original_po.partner_shipping_id.id,
            'purchase_source': original_po.purchase_source,
            'po_reference': original_po.po_reference,
        })[0]

        # Create the new RFQ with lines in one go
        new_rfq = self.env['purchase.order'].create(po_vals)

        # Remove selected lines from original PO
        selected_lines.unlink()

        return {
            'name': _('New RFQ'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': new_rfq.id,
            'target': 'current',
        }
