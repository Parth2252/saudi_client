# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmStage(models.Model):
    _inherit = "crm.stage"

    is_confirm_sale_order_created_state = fields.Boolean(copy=False)
    is_po_confirm_state = fields.Boolean(copy=False)
    is_vendor_bill_created_state = fields.Boolean(copy=False)
    is_vendor_bill_paid_state = fields.Boolean(copy=False)
    is_goods_received_state = fields.Boolean(copy=False)
    is_customer_delivered_state = fields.Boolean(copy=False)
    is_grn_entered_state = fields.Boolean(copy=False)
    is_customer_invoiced_state = fields.Boolean(copy=False)
    is_customer_invoice_paid_state = fields.Boolean(copy=False)

