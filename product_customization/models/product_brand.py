# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'
    _sql_constraints = [
        ('unique_brand_name', 'unique(name)', 'Brand Name must be unique!')
    ]

    name = fields.Char(string="Brand Name",copy=False)
    
    
    