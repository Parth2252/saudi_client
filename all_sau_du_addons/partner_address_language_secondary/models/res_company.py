# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    name_lang2 = fields.Char()
    street1_lang2 = fields.Char()
    street2_lang2 = fields.Char()
    city_lang2 = fields.Char()
    country_lang2 = fields.Char()

