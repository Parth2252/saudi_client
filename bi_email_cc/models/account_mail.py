# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class AccountMoveSend(models.TransientModel):
    _inherit = 'account.move.send.wizard'

    cc_partner_ids = fields.Many2many('res.partner', 'account_invoice_send_res_p_ids_rel', 'wizard_id', 'p_id',
                                      string='CC')
    bcc_partner_ids = fields.Many2many('res.partner', 'account_invoice_send_res_part_ids_rel', 'wizard_id', 'part_id',
                                       string='BCC')
    rply_partner_id = fields.Many2one('res.partner', string='Default Reply-To')
    is_cc = fields.Boolean(string='Enable  CC', default=True)
    is_bcc = fields.Boolean(string='Enable BCC', default=True)
    is_reply = fields.Boolean(string='Enable Reply', default=True)

    @api.model
    def default_get(self, fields_list):
        results = super().default_get(fields_list)

        if self.env.company.cc_partner_ids or self.env.company.bcc_partner_ids:
            results.update({
                'rply_partner_id': self.env.company.rply_partner_id.id if self.env.company.rply_partner_id else False,
                'cc_partner_ids': [(6, 0, self.env.company.cc_partner_ids.ids)],
                'bcc_partner_ids': [(6, 0, self.env.company.bcc_partner_ids.ids)],
                'is_cc': self.env.company.email_cc,
                'is_bcc': self.env.company.email_bcc,
                'is_reply': self.env.company.email_reply,
            })
        else:
            results.update({
                'rply_partner_id': self.env.company.rply_partner_id if self.env.company.rply_partner_id else False,
                'is_cc': self.env.company.email_cc,
                'is_bcc': self.env.company.email_bcc,
                'is_reply': self.env.company.email_reply,
            })
        return results
