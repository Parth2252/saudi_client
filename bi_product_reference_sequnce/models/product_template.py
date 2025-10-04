# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bi_available_categ_ids = fields.Many2many('product.category', 'Availabe Category',
        compute='_compute_active_category')
    bi_sequence = fields.Many2one('ir.sequence', related="categ_id.bi_sequence", string="SQ")

    @api.depends('categ_id')
    def _compute_active_category(self):
        for rec in self:
            categ_ids = self.env['product.category'].search([('bi_active','=',True)])
            rec.bi_available_categ_ids = categ_ids

    @api.model_create_multi
    def create(self, vals_list):
        for data in vals_list:
            categ_id = self.env['product.category'].browse(data.get('categ_id'))
            sequence_id = categ_id.bi_sequence
            if sequence_id:
                code = sequence_id.next_by_code(sequence_id.code)
                data['default_code'] = code
        return super(ProductTemplate, self).create(vals_list)

    def write(self, vals):
        categ_id = self.env['product.category'].browse(vals.get('categ_id'))
        sequence_id = categ_id.bi_sequence
        if sequence_id:
            code = sequence_id.next_by_code(sequence_id.code)
            vals['default_code'] = code
        return super(ProductTemplate, self).write(vals)


class ProductProduct(models.Model):
    _inherit = "product.product"

    bi_available_categ_ids = fields.Many2many('product.category', 'Availabe Category',
        compute='_compute_active_category')
    bi_sequence = fields.Many2one('ir.sequence', related="categ_id.bi_sequence", string="SQ")

    @api.depends('categ_id')
    def _compute_active_category(self):
        for rec in self:
            categ_ids = self.env['product.category'].search([('bi_active','=',True)])
            rec.bi_available_categ_ids = categ_ids

    @api.model_create_multi
    def create(self, vals_list):
        for data in vals_list:
            product_tmpl_id = data.get('product_tmpl_id')
            if not data.get('categ_id') and product_tmpl_id:
                product_tmpl = self.env['product.template'].browse(product_tmpl_id)
                data['categ_id'] = product_tmpl.categ_id.id
            categ_id = self.env['product.category'].browse(data.get('categ_id'))
            sequence_id = categ_id.bi_sequence
            if sequence_id:
                code = sequence_id.next_by_code(sequence_id.code)
                data['default_code'] = code
        return super(ProductProduct, self).create(vals_list)

    def write(self, vals):
        print("write",vals)
        categ_id = self.env['product.category'].browse(vals.get('categ_id'))
        sequence_id = categ_id.bi_sequence
        if sequence_id:
            code = sequence_id.next_by_code(sequence_id.code)
            vals['default_code'] = code
        return super(ProductProduct, self).write(vals)
