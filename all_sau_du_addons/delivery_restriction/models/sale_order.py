from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_status = fields.Selection(
        [
            ("pending", "Not Delivered"),
            ("started", "Started"),
            ("partial", "Partially Delivered"),
            ("delivered", "Delivered"),
            ("full", "Fully Delivered"),
        ],
        string="Delivery Status",
        compute="_compute_delivery_status",
        store=True,
        help="Blue: Not Delivered/Started\n\
            Orange: Partially Delivered\n\
            Green: Fully Delivered",
    )

    @api.depends("picking_ids", "picking_ids.state")
    def _compute_delivery_status(self):
        for order in self:
            if not order.picking_ids or all(
                p.state == "cancel" for p in order.picking_ids
            ):
                order.delivery_status = False
            elif all(p.state in ["done", "cancel"] for p in order.picking_ids):
                order.delivery_status = "full"
            elif any(p.state == "done" for p in order.picking_ids) and any(
                l.qty_delivered for l in order.order_line
            ):
                order.delivery_status = "partial"
            elif any(p.state == "done" for p in order.picking_ids):
                order.delivery_status = "started"
            elif any(p.state == "delivered" for p in order.picking_ids):
                order.delivery_status = "delivered"
            else:
                order.delivery_status = "pending"

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()

        # Filter pickings in 'done' state and with a GR number
        done_pickings = self.picking_ids.filtered(lambda p: p.state == 'done' and p.gr_number and p.date_done)

        # Sort by the actual date_done (i.e., validation time)
        if done_pickings:
            latest_picking = done_pickings.sorted('date_done')[-1]  # Latest by date_done
            invoice_vals['gr_number'] = latest_picking.gr_number

        return invoice_vals

