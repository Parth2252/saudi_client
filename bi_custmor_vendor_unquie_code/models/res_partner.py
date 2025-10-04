# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    customer_code = fields.Char('Customer Code', company_dependent=True, store=True)
    vendor_code = fields.Char('Vendor Code', company_dependent=True, store=True)
    beneficiary_currency = fields.Many2one('res.currency', string='Beneficiary Currency')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ResPartner, self).create(vals_list)
        for record in records:
            if record.customer_rank != 0:
                sequence_code = self.env['ir.sequence'].sudo().next_by_code('customer.code')
                record.customer_code = sequence_code or _('New')
            if record.supplier_rank != 0:
                sequence_code = self.env['ir.sequence'].sudo().next_by_code('vendor.code')
                record.vendor_code = sequence_code or _('New')
        return records
