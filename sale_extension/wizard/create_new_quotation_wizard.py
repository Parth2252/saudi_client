from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError

class CreateNewQuotationWizard(models.TransientModel):
    _name = 'create.new.quotation.wizard'
    _description = 'Create New Quotation from Selected Lines'

    sale_id = fields.Many2one('sale.order', string='Original Quotation', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    warning_message = fields.Text(string="Warning", readonly=True, default="Note: All details (except Customer) and selected lines will be copied from the current Quotation. Selected lines will be removed from the original Quotation.")

    @api.model
    def default_get(self, fields):
        res = super(CreateNewQuotationWizard, self).default_get(fields)
        if self._context.get('active_id'):
            sale = self.env['sale.order'].browse(self._context.get('active_id'))
            res.update({
                'sale_id': sale.id,
                'partner_id': sale.partner_id.id,
            })
        return res

    def action_create_quotation(self):
        self.ensure_one()
        original_so = self.sale_id
        selected_lines = original_so.order_line.filtered(lambda l: l.select_for_new_quotation and not l.display_type)

        if not selected_lines:
            raise UserError(_("Please select at least one line to create a new Quotation."))

        # Prepare line values using Command pattern
        new_lines_vals = []
        for line in selected_lines:
            line_vals = line.copy_data({
                'select_for_new_quotation': False,
                'delivery_date': line.delivery_date, # copy=False in model
            })[0]
            new_lines_vals.append(Command.create(line_vals))

        # Prepare SO values
        so_vals = original_so.copy_data({
            'partner_id': self.partner_id.id,
            'order_line': new_lines_vals,
            'state': 'draft',
            'origin': original_so.name,
            'quote_desc': original_so.quote_desc,
            'contact_id': original_so.contact_id.id,
            'commitment_date': original_so.commitment_date,
            'po_expire_date': original_so.po_expire_date,
            'validity_date': original_so.validity_date,
            'client_order_ref': original_so.client_order_ref,
        })[0]

        # Create the new Quotation with lines in one go
        new_so = self.env['sale.order'].create(so_vals)

        # Remove selected lines from original SO
        selected_lines.unlink()

        return {
            'name': _('New Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': new_so.id,
            'target': 'current',
        }
