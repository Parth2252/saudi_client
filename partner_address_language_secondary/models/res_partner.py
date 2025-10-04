# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    name_lang2 = fields.Char(copy=False)
    street1_lang2 = fields.Char(copy=False)
    street2_lang2 = fields.Char(copy=False)
    city_lang2 = fields.Char(copy=False)
    country_lang2 = fields.Many2one('res.country', string='Country', copy=False)
    cr_number = fields.Char(copy=False, string='CR Number')




