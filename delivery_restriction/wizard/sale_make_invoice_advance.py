# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models
from odoo.exceptions import ValidationError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        res = super().create_invoices()
        sale_order_env = self.env["sale.order"]
        sale_order_id = sale_order_env.browse(self._context.get("active_id"))
        if (
            not sale_order_id.delivery_status == "full"
            and not sale_order_id.partner_id.is_allowed_partial_delivery_payment
        ):
            raise ValidationError(
                _(
                    "You cannot create the invoice. Please delivered the product to create the invoice."
                )
            )
        return res
