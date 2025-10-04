# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    boxes_qty = fields.Float(string="Boxes Qty")
    gross_weight = fields.Float(string="Gross Weight (kg)")
    pallet_qty = fields.Float(string="Pallet Qty")
    sr_no_do = fields.Integer(
        string="Order No", readonly=False, compute="_compute_sr_no_do", store=True
    )
    po_ref_do = fields.Char(string="PO Ref")
    po_ref = fields.Char(string="PO Ref")
    part_no = fields.Char(string="Part No")
    manuanl_qty = fields.Integer(string="Quantity")
    manuanl_remark = fields.Char(string="Remark")

    validated_datetime = fields.Datetime(string="Validated On")
    validated_by_id = fields.Many2one("res.users", string="Validated By", readonly=True)
    validated_employee_id = fields.Many2one(
        "hr.employee",
        string="Validated Employee",
        compute="_compute_validated_employee",
        store=True,
    )
    offered_description_id = fields.Many2one(
        "product.product",
        string="Offered Description",
        related="sale_line_id.offered_description_id",
        store=True,
        readonly=False,
    )

    # customization start.
    delivery_date = fields.Datetime(copy=False)
    # customization end.

    def stock_move_line_sequence(self):
        number = 1
        for record in self.picking_id.move_ids_without_package:
            record.sr_no_do = number
            number += 1

    # @api.model_create_multi
    # def create(self, vals_list):
    #     """Auto-create sequence for purchase order lines."""
    #     lines = super().create(vals_list)
    #     for line in lines:
    #         if not line.sale_line_id and not line.purchase_line_id:
    #             line.stock_move_line_sequence()
    #     return lines

    @api.depends("validated_by_id")
    def _compute_validated_employee(self):
        for rec in self:
            employee = self.env["hr.employee"].search(
                [("user_id", "=", rec.validated_by_id.id)], limit=1
            )
            rec.validated_employee_id = employee

    def button_validate(self):
        res = super().button_validate()

        for picking in self:
            if picking.state == "done":
                picking.validated_by_id = self.env.user
                picking.validated_datetime = fields.Datetime.now()

        return res

    def _get_new_picking_values(self):
        """ Method for passing value from sale order to stock move or picking. """
        vals = super(StockMove, self)._get_new_picking_values()
        so = self.sale_line_id.order_id
        vals["partner_invoice_id"] = so.partner_invoice_id.id
        vals["contact_id"] = so.partner_shipping_id.id
        vals["partner_id"] = so.partner_id.id
        vals["porder_ref"] = so.client_order_ref
        return vals

    @api.depends("sale_line_id", "purchase_line_id")
    def _compute_sr_no_do(self):
        """se the sequence from salr order to delivery and purchase to receipt. """
        for move in self:
            if move.sale_line_id:
                move.sr_no_do = move.sale_line_id.sr_no_so
            elif move.purchase_line_id:
                move.sr_no_do = move.purchase_line_id.sr_no_po

