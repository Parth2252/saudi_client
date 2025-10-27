# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    partner_product_line_ids = fields.One2many('partner.product.line','partner_id',string="Partner Product Line")