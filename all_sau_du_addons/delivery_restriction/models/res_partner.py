from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_allowed_partial_delivery_payment = fields.Boolean(
        string="Is Allowed Partial Delivery Payment?", copy=False
    )
