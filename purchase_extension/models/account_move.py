from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"
    
    purchase_source = fields.Selection(
        [
            ("standard", "Standard Purchase"),
            ("local", "Local Purchase"),
            ("online", "Online Purchase"),
        ],
        string="Purchase Source",
    )