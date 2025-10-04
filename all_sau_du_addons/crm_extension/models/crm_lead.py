import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import format_date
from babel.numbers import format_currency


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    contact_id = fields.Many2one('res.partner', 'Customer Contact')
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain=[('is_company', '=', True)],
    )