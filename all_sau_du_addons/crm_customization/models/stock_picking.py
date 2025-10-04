# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    opportunity_id = fields.Many2one("crm.lead", string="Opportunity", copy=False)

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            # ========== Vendor Incoming Picking ==========
            if picking.purchase_id and picking.purchase_id.opportunity_id and picking.picking_type_id.code == "incoming":
                opportunity = picking.purchase_id.opportunity_id
                all_pos = self.env["purchase.order"].search([
                    ("opportunity_id", "=", opportunity.id)
                ])
                stock_picking_ids = all_pos.mapped("picking_ids").filtered(lambda p: p.picking_type_id.code == "incoming")

                all_done = all(pick.state == "done" for pick in stock_picking_ids)

                if all_done and stock_picking_ids:
                    goods_received_from_supplier = self.env["crm.stage"].search(
                        [("is_goods_received_state", "=", True)], limit=1
                    )
                    if goods_received_from_supplier:
                        opportunity.stage_id = goods_received_from_supplier.id

            # ========== Customer Outgoing Picking ==========
            if picking.opportunity_id and picking.picking_type_id.code == "outgoing":
                opportunity = picking.opportunity_id
                all_sos = self.env["sale.order"].search([
                    ("opportunity_id", "=", opportunity.id)
                ])
                stock_picking_ids = all_sos.mapped("picking_ids").filtered(lambda p: p.picking_type_id.code == "outgoing")

                all_done = all(pick.state == "done" for pick in stock_picking_ids)

                if all_done and stock_picking_ids:
                    entered_grn_customer_delivered = self.env["crm.stage"].search(
                        [("is_grn_entered_state", "=", True)], limit=1
                    )
                    if entered_grn_customer_delivered:
                        opportunity.stage_id = entered_grn_customer_delivered.id

        return res


    def confirm_gr_number(self):
        for picking in self:
            picking.state = "delivered"

            if picking.opportunity_id and picking.picking_type_id.code == "outgoing":
                opportunity = picking.opportunity_id

                all_sos = self.env["sale.order"].search([
                    ("opportunity_id", "=", opportunity.id)
                ])

                all_outgoing_pickings = all_sos.mapped("picking_ids").filtered(
                    lambda p: p.picking_type_id.code == "outgoing"
                )

                all_delivered = all(pick.state == "delivered" for pick in all_outgoing_pickings)

                if all_delivered and all_outgoing_pickings:
                    goods_deliver_to_customer = self.env["crm.stage"].search(
                        [("is_customer_delivered_state", "=", True)], limit=1
                    )
                    if goods_deliver_to_customer:
                        opportunity.stage_id = goods_deliver_to_customer.id
                else:
                    goods_received = self.env["crm.stage"].search(
                        [("is_goods_received_state", "=", True)], limit=1
                    )
                    if goods_received:
                        opportunity.stage_id = goods_received.id

