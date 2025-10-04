from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "account.move"

    gr_number = fields.Char(string="GR Number", size=15, copy=False)

    @api.constrains("gr_number")
    def _check_gr_number(self):
        for move in self:
            if move.gr_number and not move.gr_number.isdigit():
                raise ValidationError(_("The GR Number must contain only digits."))

    def action_post(self):
        if not self.gr_number and self.move_type == 'out_invoice':
            raise ValidationError("Please set the GR number!")
        return super().action_post()


