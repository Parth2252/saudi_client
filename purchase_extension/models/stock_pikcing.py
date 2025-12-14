from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    purchase_source = fields.Selection(
        [
            ("standard", "Standard Purchase"),
            ("local", "Local Purchase"),
            ("online", "Online Purchase"),
        ],
        string="Purchase Source",
    )