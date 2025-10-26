# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    part_no = fields.Char(string="Part Number",copy=False)
    brand_id = fields.Many2one('product.brand',string="Brand")

    
    