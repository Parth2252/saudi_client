# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountAsset(models.Model):
	_inherit = 'product.category'

	bi_sequence = fields.Many2one('ir.sequence', string="Sequence")
	bi_active = fields.Boolean(string="Active / Inactive")