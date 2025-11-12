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
