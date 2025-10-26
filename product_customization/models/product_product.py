# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    part_no = fields.Char(string="Part Number",copy=False)
    brand_id = fields.Many2one('product.brand',string="Brand")
    
    