# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_code_prefix = fields.Char(
        'Customer Prefix', related='company_id.customer_code_prefix', readonly=False)
    vendor_code_prefix = fields.Char(
        'Vendor Prefix', related='company_id.vendor_code_prefix', readonly=False)

    def action_generate_code(self):
        companies = self.env.company
        res_partner_ids = self.env['res.partner'].search([])

        if not self.customer_code_prefix and not self.vendor_code_prefix:
            raise ValidationError(_("Prefix is Mandatory."))
        else:
            for company in companies:
                customer_prefix = company.customer_code_prefix
                vendor_prefix = company.vendor_code_prefix
                check_customer_sequence = self.env['ir.sequence'].search(
                    [('code', '=', 'customer.code'), ('company_id', '=', company.id)], limit=1)
                check_vendor_sequence = self.env['ir.sequence'].search(
                    [('code', '=', 'vendor.code'), ('company_id', '=', company.id)], limit=1)

                customer_sequence = None
                vendor_sequence = None

                if customer_prefix:
                    if not check_customer_sequence:
                        customer_sequence = self.env['ir.sequence'].sudo().create({
                            'name': f'Customer Code Sequence {company.name}',
                            'code': 'customer.code',
                            'prefix': customer_prefix,
                            'padding': 5,
                            'company_id': company.id,
                        })
                    else:
                        customer_sequence = check_customer_sequence
                        customer_sequence.sudo().write({'prefix': customer_prefix, 'number_next_actual': 1})
                elif check_customer_sequence:
                    check_customer_sequence.sudo().write({'prefix': False, 'number_next_actual': 1})
                    res_partner_ids.sudo().write({'customer_code': False})

                if vendor_prefix:
                    if not check_vendor_sequence:
                        vendor_sequence = self.env['ir.sequence'].sudo().create({
                            'name': f'Vendor Code Sequence {company.name}',
                            'code': 'vendor.code',
                            'prefix': vendor_prefix,
                            'padding': 5,
                            'company_id': company.id,
                        })
                    else:
                        vendor_sequence = check_vendor_sequence
                        vendor_sequence.sudo().write({'prefix': vendor_prefix, 'number_next_actual': 1})
                elif check_vendor_sequence:
                    check_vendor_sequence.sudo().write({'prefix': False, 'number_next_actual': 1})
                    res_partner_ids.sudo().write({'vendor_code': False})

                for partner in self.env['res.partner'].search([]):
                    if partner.customer_rank != 0 and customer_sequence:
                        partner.customer_code = customer_sequence.next_by_id()
                    if partner.supplier_rank != 0 and vendor_sequence:
                        partner.vendor_code = vendor_sequence.next_by_id()

        return True
