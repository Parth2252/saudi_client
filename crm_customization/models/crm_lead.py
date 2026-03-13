# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    date_deadline = fields.Datetime("Expected Closing", help="Estimate of the date on which the opportunity will be won.")
    expected_closing_status = fields.Char(compute='_compute_expected_closing_status', store=True, string="Closing Status")
    show_expected_closing = fields.Boolean(related='stage_id.show_expected_closing')

    @api.depends('date_deadline')
    def _compute_expected_closing_status(self):
        for record in self:
            if record.date_deadline:
                now = fields.Datetime.now()
                if record.date_deadline > now:
                    delta = record.date_deadline - now
                    if delta.days > 0:
                        record.expected_closing_status = f"{delta.days} {'days' if delta.days > 1 else 'day'} left"
                    else:
                        hours = delta.seconds // 3600
                        minutes = (delta.seconds % 3600) // 60
                        record.expected_closing_status = f"0 days and {hours} hrs {minutes} mins left"
                else:
                    delta = now - record.date_deadline
                    if delta.days > 0:
                        record.expected_closing_status = f"{delta.days} {'days' if delta.days > 1 else 'day'} delay"
                    else:
                        hours = delta.seconds // 3600
                        minutes = (delta.seconds % 3600) // 60
                        record.expected_closing_status = f"0 days and {hours} hrs {minutes} mins delay"
            else:
                record.expected_closing_status = False

    @api.model
    def _cron_update_expected_closing_status(self):
        leads = self.search([('active', '=', True), ('date_deadline', '!=', False)])
        for lead in leads:
            lead._compute_expected_closing_status()
    @api.model
    def retrieve_crm_dashboard(self, domain=None):
        self.browse().check_access("read")
        today = fields.Datetime.now()
        
        from odoo.osv import expression
        if domain is None:
            domain = []

        # Safely remove dashboard-specific filters from domain.
        # We need to filter out conditions on 'stage_id', 'date_deadline', and our custom search filters
        # to ensure dashboard counts reflect global context (like 'My Pipeline') but not the current dash button.
        def _is_dash_filter(node):
            if isinstance(node, (list, tuple)) and len(node) == 3:
                return node[0] in ('stage_id.name', 'date_deadline', 'probability')
            return False

        # Normalize the domain to handle complex expressions, then filter leaf nodes.
        # If it's a simple list of tuples, this is easy. If it has operators, we need to be careful.
        if domain:
            try:
                # If it's just a list of tuples, we can filter blindly.
                # If it has operators, we'd need to rebuild the tree. 
                # For basic dashboard usage, we'll assume a list of tuples or normalized list.
                base_domain = [d for d in domain if not _is_dash_filter(d) and d not in ('&', '|', '!')]
            except Exception:
                base_domain = []
        else:
            base_domain = []

        # Open RFQ: Stage 'New RFQ'
        open_rfq = self.search(expression.AND([base_domain, [
            ('stage_id.name', 'ilike', 'New RFQ'),
        ]]))
        
        # Submitted Offer: Stage 'Offer Submitted'
        submitted_offer = self.search(expression.AND([base_domain, [
            ('stage_id.name', 'ilike', 'Offer Submitted'),
        ]]))

        # Order Confirmed: Stage contains 'Won' or 'Sale Order Created'
        order_confirmed = self.search(expression.AND([base_domain, [
            '|', ('stage_id.name', 'ilike', '%Won%'), ('stage_id.name', 'ilike', '%Sale Order Created%'),
        ]]))

        # Delayed RFQ: Expected Closing < Today and stage is 'New RFQ'
        delayed_rfq = self.search(expression.AND([base_domain, [
            ('date_deadline', '<', today),
            ('stage_id.name', 'ilike', 'New RFQ'),
            ('probability', '<', 100),
        ]]))



        from odoo.tools import format_amount
        currency = self.env.company.currency_id

        def get_data(records):
            return {
                'count': len(records),
                'total': format_amount(self.env, sum(records.mapped('expected_revenue')), currency)
            }

        return {
            'open_rfq': get_data(open_rfq),
            'submitted_offer': get_data(submitted_offer),
            'order_confirmed': get_data(order_confirmed),
            'delayed_rfq': get_data(delayed_rfq),
        }
