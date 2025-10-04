from odoo import models, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order"

    @api.onchange("client_order_ref")
    def onchange_client_order_ref(self):
        sale_env = self.env["sale.order"]
        if not self.client_order_ref:
            return
        po_ref_available_record_sale = sale_env.search(
            [("client_order_ref", "=", self.client_order_ref)], limit=1
        )
        po_env = self.env["purchase.order"]
        po_ref_available_record_purchase = po_env.search(
            [("po_reference", "=", self.client_order_ref)], limit=1
        )
        if po_ref_available_record_sale:
            raise ValidationError(
                "This purchase order reference value is already available in sale order: %s"
                % po_ref_available_record_sale.name
            )
        elif po_ref_available_record_purchase:
            raise ValidationError(
                "This purchase order reference value is already available in purchase order: %s"
                % po_ref_available_record_purchase.name
            )
