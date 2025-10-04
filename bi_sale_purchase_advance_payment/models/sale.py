# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    account_payment_ids = fields.One2many('account.payment', 'sale_id', string="Pay sale advanced", readonly=True, groups="account.group_account_invoice,account.group_account_readonly")

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(AccountMove, self).action_post()
        allow_auto_reconcile_sale = self.env['res.config.settings'].sudo().get_values().get('allow_auto_reconcile_sale')
        allow_auto_reconcile_purchase = self.env['res.config.settings'].sudo().get_values().get('allow_auto_reconcile_purchase')


        if allow_auto_reconcile_sale:
            for move in self:
                if move.move_type == 'out_invoice' and move.invoice_origin:
                    sale_order_id = self.env['sale.order'].search([('name', '=', move['invoice_origin'])], limit=1)
                    if sale_order_id.account_payment_ids:
                        for rec in sale_order_id.account_payment_ids:
                            if rec.is_reconciled == False:
                                for record in rec:
                                    (move + record.move_id).line_ids.filtered(lambda line: line.account_id == record.destination_account_id and not line.reconciled).reconcile()

        if allow_auto_reconcile_purchase:
            for move in self:
                if move.move_type == 'in_invoice' and move.invoice_origin:
                    purchase_order_id = self.env['purchase.order'].search([('name', '=', move['invoice_origin'])], limit=1)
                    if purchase_order_id.account_payment_ids:
                        for rec in purchase_order_id.account_payment_ids:
                            if rec.is_reconciled == False:
                                for record in rec:
                                    (move + record.move_id).line_ids.filtered(lambda line: line.account_id == record.destination_account_id and not line.reconciled).reconcile()

        else:
            return res
