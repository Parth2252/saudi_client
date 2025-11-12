# -*- coding: utf-8 -*-
# Part of The Stella Technolabs. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string="Customer")
    is_vendor = fields.Boolean(string="Vendor")
    customer_code = fields.Char('Customer Code', company_dependent=True, store=True)
    vendor_code = fields.Char('Vendor Code', company_dependent=True, store=True)

    @api.constrains('is_customer', 'is_vendor')
    def check_customer_vendor(self):
        for rec in self:
            if rec.is_customer and not rec.customer_code:
                customer_seq = self.env['ir.sequence'].next_by_code('customer.code.cust') or '/'
                prefix = self.env.company.customer_code_prefix or ''
                rec.customer_code = prefix + customer_seq
            if rec.is_vendor and not rec.vendor_code:
                vendor_seq = self.env['ir.sequence'].next_by_code('vendor.code.cust') or '/'
                prefix = self.env.company.vendor_code_prefix or ''
                rec.vendor_code = prefix + vendor_seq

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            context_move_type = self.env.context.get('default_move_type')
            if context_move_type in ['out_invoice', 'out_refund']:
                vals['is_customer'] = True
            elif context_move_type in ['in_invoice', 'in_refund']:
                vals['is_vendor'] = True
        return super().create(vals_list)

    def _generate_missing_customer_vendor_codes(self):
        sale_customer_ids = self.env['sale.order'].search([]).mapped('partner_id').ids
        purchase_vendor_ids = self.env['purchase.order'].search([]).mapped('partner_id').ids
        partners = self.search([
            '|',
            ('id', 'in', sale_customer_ids),
            ('id', 'in', purchase_vendor_ids)
        ])
        for partner in partners:
            if partner.id in sale_customer_ids:
                partner.is_customer = True
                if not partner.customer_code:
                    customer_seq = self.env['ir.sequence'].next_by_code('customer.code.cust') or '/'
                    prefix = partner.company_id.customer_code_prefix or ''
                    partner.customer_code = prefix + customer_seq
            if partner.id in purchase_vendor_ids:
                partner.is_vendor = True
                if not partner.vendor_code:
                    vendor_seq = self.env['ir.sequence'].next_by_code('vendor.code.cust') or '/'
                    prefix = partner.company_id.vendor_code_prefix or ''
                    partner.vendor_code = prefix + vendor_seq
