# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
	_inherit = 'res.users'

	is_mail_by_company = fields.Boolean(string='Is Mail By Company', default=False)
