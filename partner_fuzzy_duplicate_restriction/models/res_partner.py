import difflib
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    force_new_contact = fields.Boolean(
        string="Force Create New Customer/Supplier",
        default=False,
        help="Check this box to bypass the 80% similarity duplicate name check."
    )

    duplicate_contact_count = fields.Integer(
        string='Similar Contacts', 
        compute='_compute_duplicate_contact_count'
    )

    def _get_fuzzy_duplicate_domain(self):
        """Returns domain of duplicates to display in standard views if clicked"""
        self.ensure_one()
        if not self.name:
            return [('id', 'in', [])]
        
        existing_partners = self.sudo().search_read(
            [('name', '!=', False), ('active', 'in', [True, False]), ('id', '!=', self.id)],
            ['id', 'name'],
            limit=50000
        )
        
        name_to_check = str(self.name).lower().strip()
        duplicate_ids = []
        for ex in existing_partners:
            if ex.get('name'):
                lower_name = str(ex['name']).lower().strip()
                ratio = difflib.SequenceMatcher(None, name_to_check, lower_name).ratio()
                if ratio >= 0.8:
                    duplicate_ids.append(ex['id'])
                    
        return [('id', 'in', duplicate_ids)]

    def _compute_duplicate_contact_count(self):
        for partner in self:
            if not partner.id or not partner.name:
                partner.duplicate_contact_count = 0
                continue
            
            existing_partners = partner.sudo().search_read(
                [('name', '!=', False), ('active', 'in', [True, False]), ('id', '!=', partner.id)],
                ['id', 'name'],
                limit=50000
            )
            
            name_to_check = str(partner.name).lower().strip()
            count = 0
            for ex in existing_partners:
                if ex.get('name'):
                    lower_name = str(ex['name']).lower().strip()
                    ratio = difflib.SequenceMatcher(None, name_to_check, lower_name).ratio()
                    if ratio >= 0.8:
                        count += 1
            
            partner.duplicate_contact_count = count

    def action_view_duplicate_contacts(self):
        self.ensure_one()
        domain = self._get_fuzzy_duplicate_domain()
        
        return {
            'name': _('Similar Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'active_test': False, 'create': False},
        }

    @api.model_create_multi
    def create(self, vals_list):
        existing_partners = self.sudo().search_read(
            [('name', '!=', False), ('active', 'in', [True, False])],
            ['name'],
            limit=50000
        )
        existing_names = [(str(ex['name']).strip(), str(ex['name']).lower().strip()) for ex in existing_partners if ex.get('name')]
        
        for vals in vals_list:
            if vals.get('name') and not vals.get('force_new_contact'):
                name_to_check = str(vals['name']).lower().strip()
                
                # Direct check
                exact_matches = [name for name, lower_name in existing_names if lower_name == name_to_check]
                if exact_matches:
                    raise ValidationError(_(
                        "A contact with the exact name '%s' already exists.\n"
                        "If you are sure this is a new contact, please enable the checkbox 'Force Create New Customer/Supplier' and try again."
                    ) % exact_matches[0])
                
                # Fuzzy check
                for ex_name, lower_name in existing_names:
                    ratio = difflib.SequenceMatcher(None, name_to_check, lower_name).ratio()
                    if ratio >= 0.8:
                        raise ValidationError(_(
                            "A contact with a similar name '%s' already exists (%.0f%% match).\n"
                            "If you are sure this is a new contact, please enable the checkbox 'Force Create New Customer/Supplier' and try again."
                        ) % (ex_name, ratio * 100))
                            
        return super().create(vals_list)

    @api.constrains('customer_code', 'vendor_code')
    def _check_unique_codes(self):
        for record in self:
            if record.customer_code and record.customer_code != 'New':
                if self.search_count([('customer_code', '=', record.customer_code), ('id', '!=', record.id)]) > 0:
                    raise ValidationError(_("Duplicate Customer ID detected: %s. Please use a unique Customer ID.") % record.customer_code)
            
            if record.vendor_code and record.vendor_code != 'New':
                if self.search_count([('vendor_code', '=', record.vendor_code), ('id', '!=', record.id)]) > 0:
                    raise ValidationError(_("Duplicate Vendor ID detected: %s. Please use a unique Vendor ID.") % record.vendor_code)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'customer_code': False,
            'vendor_code': False,
        })
        return super(ResPartner, self).copy(default)

    def action_rectify_duplicate_codes(self):
        """ Rectifies existing duplicate customer and vendor codes by re-generating them using the sequence """
        for record in self:
            if record.customer_code and record.customer_code != 'New':
                duplicates = self.search([('customer_code', '=', record.customer_code), ('id', '!=', record.id)])
                for dup in duplicates:
                    seq = self.env['ir.sequence'].sudo().next_by_code('customer.code')
                    if seq:
                        dup.customer_code = seq

            if record.vendor_code and record.vendor_code != 'New':
                duplicates = self.search([('vendor_code', '=', record.vendor_code), ('id', '!=', record.id)])
                for dup in duplicates:
                    seq = self.env['ir.sequence'].sudo().next_by_code('vendor.code')
                    if seq:
                        dup.vendor_code = seq
