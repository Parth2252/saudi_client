from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    gr_number = fields.Char(string="GR Number", size=15, copy=False)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("waiting", "Waiting Another Operation"),
            ("confirmed", "Waiting"),
            ("assigned", "Ready"),
            ("delivered", "Delivered"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        compute="_compute_state",
        copy=False,
        index=True,
        readonly=True,
        store=True,
        tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
        " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
        ' * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is "As soon as possible": no product could be reserved.\n(b) The shipping policy is "When all products are ready": not all the products could be reserved.\n'
        ' * Ready: The transfer is ready to be processed.\n(a) The shipping policy is "As soon as possible": at least one product has been reserved.\n(b) The shipping policy is "When all products are ready": all product have been reserved.\n'
        " * Delivered: Ready for the delivered. \n"
        " * Done: The transfer has been processed.\n"
        " * Cancelled: The transfer has been cancelled.",
    )

    @api.constrains("gr_number")
    def _check_gr_number(self):
        for picking in self:
            if picking.gr_number and not picking.gr_number.isdigit():
                raise ValidationError(_("The GR Number must contain only digits."))

    def confirm_gr_number(self):
        for picking in self:
            # if not self.gr_number:
            #     raise ValidationError("Please set the GR number!")
            picking.state = 'delivered'

    def button_validate(self):
        if not self.gr_number:
            raise ValidationError("Please set the GR number!")
        return super().button_validate()
