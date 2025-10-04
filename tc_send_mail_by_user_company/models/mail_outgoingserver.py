# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _,modules
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    smtp_config = fields.Selection([('by_user', "By User"), ('by_company', "By Company")], string='SMTP Configuration',
                                   default="by_user", required=True)
    user_id = fields.Many2one('res.users', string='User')
    company_id = fields.Many2one('res.company', string='Company')

    @api.constrains('user_id', 'company_id')
    def _check_mail_server(self):
        if self.user_id:
            mail_server_id = self.sudo().search([('user_id', '=', self.user_id.id)])
            if len(mail_server_id) > 1:
                raise ValidationError(_("You can create only one record using this user"))
        if self.company_id:
            mail_server_id = self.sudo().search([('company_id', '=', self.company_id.id)])
            if len(mail_server_id) > 1:
                raise ValidationError(_("You can create only one record using this company"))
    
    @api.onchange('smtp_config')
    def _onchage_smtp_configuration(self):
        for rec in self:
            if rec.smtp_config == 'by_user':
                rec.company_id = False
            elif rec.smtp_config == 'by_company':
                rec.user_id = False
            else:
                rec.user_id = False
                rec.company_id = False

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False, post_send_callback=None):
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param bool raise_exception: whether to raise an exception if the
                email sending process has failed
            :param post_send_callback: an optional function, called as ``post_send_callback(ids, force=False)``,
                with the mail ids that have been sent; calls with redundant ids
                are possible
            :return: True
        """
        for mail_server_id, alias_domain_id, smtp_from, batch_ids in self._split_by_mail_configuration():
            smtp_session = None
            try:
                current_uid = self._context.get('uid')
                current_user_object = self.env['res.users'].browse(current_uid)
                user = self.env.ref('base.user_admin')
                if current_user_object.is_mail_by_company:
                    smtp_mail_server = self.env['ir.mail_server'].search(
                        [('company_id', '=', self.env.company.id)], limit=1)
                else:
                    smtp_mail_server = self.env['ir.mail_server'].search([('user_id', '=', current_uid)], limit=1)
                if not smtp_mail_server:
                    smtp_mail_server = self.env['ir.mail_server'].search([('user_id', '=', user.id)], limit=1)
                smtp_session = self.env['ir.mail_server'].connect(mail_server_id=smtp_mail_server.id, smtp_from=smtp_from)
            except Exception as exc:
                if raise_exception:
                    # To be consistent and backward compatible with mail_mail.send() raised
                    # exceptions, it is encapsulated into an Odoo MailDeliveryException
                    raise MailDeliveryException(_('Unable to connect to SMTP Server'), exc)
                else:
                    batch = self.browse(batch_ids)
                    batch.write({'state': 'exception', 'failure_reason': exc})
                    batch._postprocess_sent_message(success_pids=[], failure_type="mail_smtp")
            else:
                mail_server = self.env['ir.mail_server'].browse(mail_server_id)
                self.browse(batch_ids)._send(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    smtp_session=smtp_session,
                    alias_domain_id=alias_domain_id,
                    mail_server=mail_server,
                    post_send_callback=post_send_callback,
                )
                if not modules.module.current_test:
                    _logger.info(
                        'Sent batch %s emails via mail server ID #%s',
                        len(batch_ids), mail_server_id)
            finally:
                if smtp_session:
                    smtp_session.quit()