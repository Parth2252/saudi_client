# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for order in self:
            if order.opportunity_id:
                confirm_so_created_state = self.env["crm.stage"].search([("is_confirm_sale_order_created_state", "=", True)])
                order.opportunity_id.stage_id = confirm_so_created_state.id            
        return super(SaleOrder, self).action_confirm()


    def action_cancel(self):
        for order in self:
            if order.opportunity_id:
                current_stage = order.opportunity_id.stage_id
                if current_stage and current_stage.is_confirm_sale_order_created_state:
                    current_sequence = current_stage.sequence

                    previous_stage = self.env["crm.stage"].search(
                        [("sequence", "<", current_sequence)],
                        order="sequence desc",
                        limit=1,
                    )

                    if previous_stage:
                        order.opportunity_id.stage_id = previous_stage.id

        return super(SaleOrder, self).action_cancel()


    def _prepare_invoice(self):
        """ Method for passing value from sale order to regular invoice. """
        res = super(SaleOrder, self)._prepare_invoice()
        res["opportunity_id"] = self.opportunity_id.id
        return res