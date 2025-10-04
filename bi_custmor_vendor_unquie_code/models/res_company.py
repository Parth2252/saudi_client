# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    customer_code_prefix = fields.Char('Customer Code Prefix')
    vendor_code_prefix = fields.Char('Vendor Code Prefix')
