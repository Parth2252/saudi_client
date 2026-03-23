# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def retrieve_dashboard(self):
        """Returns the values to populate the custom dashboard in
        the stock picking views.
        """
        self.browse().check_access("read")
        today = fields.Date.context_today(self)
        company_id = self.env.company.id

        # --- RECEIPTS (Incoming) ---
        receipt_type_ids = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('company_id', '=', company_id)]).ids
        incoming_domain = [('picking_type_id', 'in', receipt_type_ids), ('company_id', '=', company_id)]

        today_receivables = self.search(incoming_domain + [('scheduled_date', '=', today), ('state', 'not in', ('done', 'delivered', 'cancel'))])
        delayed_receivables = self.search(incoming_domain + [('scheduled_date', '<', today), ('state', 'not in', ('done', 'delivered', 'cancel'))])
        received = self.search(incoming_domain + [('state', 'in', ('done', 'delivered'))])
        
        # Partially Received logic
        partially_received = self.search(incoming_domain + [('state', 'in', ('done', 'delivered')), ('backorder_ids', '!=', False)])
        
        # Pending Invoice: Done pickings where PO is 'to invoice'
        pending_invoice_receipts = self.search(incoming_domain + [('state', 'in', ('done', 'delivered')), ('purchase_id.invoice_status', '=', 'to invoice')])
        
        done_receipts = self.search(incoming_domain + [('state', 'in', ('done', 'delivered'))])

        # --- DELIVERIES (Outgoing) ---
        delivery_type_ids = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('company_id', '=', company_id)]).ids
        outgoing_domain = [('picking_type_id', 'in', delivery_type_ids), ('company_id', '=', company_id)]

        today_deliveries = self.search(outgoing_domain + [('scheduled_date', '=', today), ('state', 'not in', ('done', 'delivered', 'cancel'))])
        delayed_deliveries = self.search(outgoing_domain + [('scheduled_date', '<', today), ('state', 'not in', ('done', 'delivered', 'cancel'))])
        delivered = self.search(outgoing_domain + [('state', 'in', ('done', 'delivered'))])
        partially_delivered = self.search(outgoing_domain + [('state', 'in', ('done', 'delivered')), ('backorder_ids', '!=', False)])
        
        # Pending GRN 
        pending_grn = self.search(outgoing_domain + [('state', 'in', ('done', 'delivered')), ('sale_id.invoice_status', '=', 'to invoice')])
        
        done_deliveries = self.search(outgoing_domain + [('state', 'in', ('done', 'delivered'))])


        def get_data(records):
            return {
                'count': len(records),
            }

        result = {
            'today_receivables': get_data(today_receivables),
            'delayed_receivables': get_data(delayed_receivables),
            'received': get_data(received),
            'partially_received': get_data(partially_received),
            'pending_invoice_receipts': get_data(pending_invoice_receipts),
            'done_receipts': get_data(done_receipts),
            
            'today_deliveries': get_data(today_deliveries),
            'delayed_deliveries': get_data(delayed_deliveries),
            'delivered': get_data(delivered),
            'partially_delivered': get_data(partially_delivered),
            'pending_grn': get_data(pending_grn),
            'done_deliveries': get_data(done_deliveries),
        }
        return result
