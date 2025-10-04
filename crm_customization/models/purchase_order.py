# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    opportunity_id = fields.Many2one("crm.lead", string="Opportunity", copy=False)

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["opportunity_id"] = self.opportunity_id.id
        return res

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.opportunity_id:
                all_pos = self.env["purchase.order"].search([
                    ("opportunity_id", "=", order.opportunity_id.id)
                ])

                all_confirmed = all(po.state in ["purchase", "done"] for po in all_pos)

                if all_confirmed:
                    confirm_po_created_state = self.env["crm.stage"].search(
                        [("is_po_confirm_state", "=", True)],
                        limit=1,
                    )
                    if confirm_po_created_state:
                        order.opportunity_id.stage_id = confirm_po_created_state.id
        return res
    
    
    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        for order in self:
            if order.opportunity_id:
                confirm_so_created_state = self.env["crm.stage"].search(
                    [("is_confirm_sale_order_created_state", "=", True)],
                    limit=1,
                )
                if confirm_so_created_state:
                    order.opportunity_id.stage_id = confirm_so_created_state.id
        return res