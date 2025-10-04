# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_auto_reconcile_sale = fields.Boolean(string="Auto Reconcile Advance Payment",default=False)
    allow_auto_reconcile_purchase = fields.Boolean(string="Auto Reconcile Advance Payment ",default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefaultGet = self.env['ir.default'].sudo()._get
        allow_auto_reconcile_sale = IrDefaultGet("res.config.settings",'allow_auto_reconcile_sale')
        allow_auto_reconcile_purchase = IrDefaultGet("res.config.settings",'allow_auto_reconcile_purchase')
        res.update(
            allow_auto_reconcile_sale=allow_auto_reconcile_sale,
            allow_auto_reconcile_purchase=allow_auto_reconcile_purchase,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set("res.config.settings",'allow_auto_reconcile_sale',self.allow_auto_reconcile_sale)
        IrDefault.set("res.config.settings",'allow_auto_reconcile_purchase',self.allow_auto_reconcile_purchase)