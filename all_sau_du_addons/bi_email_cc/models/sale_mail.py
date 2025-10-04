# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, tools,_


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    cc_partner_ids = fields.Many2many('res.partner', 'mail_compose_message_res_cc_partner_rel',
                                      'wizard_id', 'cc_partner_id', 'CC', readonly=False)
    bcc_partner_ids = fields.Many2many('res.partner', 'mail_compose_message_res_bcc_partner_rel',
                                       'wizard_id', 'bcc_partner_id', 'BCC', readonly=False)
    rply_partner_id = fields.Many2one('res.partner', string='Default Reply-To', readonly=False)
    is_cc = fields.Boolean(string='Enable Email CC', default=True)
    is_bcc = fields.Boolean(string='Enable Email BCC', default=True)
    is_reply = fields.Boolean(string='Reply', default=True)

    @api.model
    def default_get(self, fields):
        res = super(MailComposeMessage, self).default_get(fields)
        if self.env.company.cc_partner_ids or self.env.company.bcc_partner_ids:
            res.update({
                'rply_partner_id': self.env.company.rply_partner_id.id if self.env.company.rply_partner_id else False,
                'cc_partner_ids': [(6, 0, self.env.company.cc_partner_ids.ids)],
                'bcc_partner_ids': [(6, 0, self.env.company.bcc_partner_ids.ids)],
                'is_cc': self.env.company.email_cc,
                'is_bcc': self.env.company.email_bcc,
                'is_reply': self.env.company.email_reply,
            })
        else:
            res.update({
                'rply_partner_id': self.env.company.rply_partner_id if self.env.company.rply_partner_id else False,
                'is_cc': self.env.company.email_cc,
                'is_bcc': self.env.company.email_bcc,
                'is_reply': self.env.company.email_reply,
            })

        return res

    def get_mail_values(self, res_ids):
        res = super(MailComposeMessage, self).get_mail_values(res_ids)
        for rec in res_ids:
            res[rec].update({
                "cc_partner_ids": [(6, 0, self.env.company.cc_partner_ids.ids)],
                "bcc_partner_ids": [(6, 0, self.env.company.bcc_partner_ids.ids)],
                "rply_partner_id": self.env.company.rply_partner_id.id,
            })
        return res
