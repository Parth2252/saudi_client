# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    partner_product_line_ids = fields.One2many('partner.product.line','partner_id',string="Partner Product Line")
    product_ids = fields.Many2many('product.product', 'res_partner_product_rel', 'partner_id', 'product_id', string="Products", compute='_compute_partner_products', store=True)
    brand_ids = fields.Many2many('product.brand', 'res_partner_brand_rel', 'partner_id', 'brand_id', string="Brands", compute='_compute_partner_products', store=True)

    @api.depends('partner_product_line_ids', 'partner_product_line_ids.product_id', 'partner_product_line_ids.brand_id')
    def _compute_partner_products(self):
        for record in self:
            record.product_ids = [fields.Command.set(record.partner_product_line_ids.mapped('product_id').ids)]
            record.brand_ids = [fields.Command.set(record.partner_product_line_ids.mapped('brand_id').ids)]

    def action_recompute_products(self):
        """Action to manually recompute stored Many2many fields for all partners."""
        partners = self.search([('partner_product_line_ids', '!=', False)])
        partners._compute_partner_products()
        return True