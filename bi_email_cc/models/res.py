# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class InheritResCompany(models.Model):
    _inherit = "res.company"

    cc_partner_ids = fields.Many2many('res.partner', 'company_id', string="Default CC")
    bcc_partner_ids = fields.Many2many('res.partner', string="Default BCC")
    email_cc = fields.Boolean(string='Enable Email CC')
    email_bcc = fields.Boolean(string='Enable Email BCC')
    email_reply = fields.Boolean(string='Enable Reply-To')
    rply_partner_id = fields.Many2one('res.partner', string='Default Reply-To')
    email = fields.Char(string="Email")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _description = "Res config Settings"

    cc_partner_ids = fields.Many2many(related="company_id.cc_partner_ids",readonly=False)
    bcc_partner_ids = fields.Many2many(related="company_id.bcc_partner_ids",readonly=False)
    email_cc = fields.Boolean(related="company_id.email_cc",readonly=False)
    email_bcc = fields.Boolean(related="company_id.email_bcc",readonly=False)
    email_reply = fields.Boolean(related="company_id.email_reply",readonly=False)
    rply_partner_id = fields.Many2one(related="company_id.rply_partner_id",readonly=False)
    email = fields.Char(related="company_id.email",readonly=False)

   