# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import logging
import psycopg2
import smtplib
from odoo import api, fields, models,_
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    cc_partner_ids = fields.Many2many('res.partner', 'mail_mail_res_p_rel', 'mail_mail_id', string=' CC(Partners)',
                                      context={'active_test': False})
    bcc_partner_ids = fields.Many2many('res.partner', 'mail_mail_part_rel', 'mail_mail_id', string='BCC(Partners)',
                                       context={'active_test': False})
    rply_partner_id = fields.Many2one('res.partner', string='Default Reply-To')
    email_bcc = fields.Char('BCc', help='Carbon copy message recipients')

    @api.model_create_multi
    def create(self, values_list):
        data = self.env["mail.compose.message"].sudo().search([], order="id desc", limit=1)
        record = self.env["account.move.send.wizard"].sudo().search([], order="id desc", limit=1)

        for values in values_list:
            if data.is_cc:
                values.update({"cc_partner_ids": [(6, 0, data.cc_partner_ids.ids)]})
            if data.is_bcc:
                values.update({"bcc_partner_ids": [(6, 0, data.bcc_partner_ids.ids)]})
            if data.is_reply:
                values.update({"rply_partner_id": int(data.rply_partner_id)})

        res = super(MailMail, self).create(values_list)
        return res

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None, alias_domain_id=False,mail_server=False, post_send_callback=None):
        IrMailServer = self.env['ir.mail_server']
        # Only retrieve recipient followers of the mails if needed
        mails_with_unfollow_link = self.filtered(lambda m: m.body_html and '/mail/unfollow' in m.body_html)
        recipients_follower_status = (
            None if not mails_with_unfollow_link
            else self.env['mail.followers']._get_mail_recipients_follower_status(mails_with_unfollow_link.ids)
        )
        email_cc_list = []
        for mail_id in self.ids:
            success_pids = []
            failure_reason = None
            failure_type = None
            processing_pid = None
            mail = None
            try:
                mail = self.browse(mail_id)
                if mail.state != 'outgoing':
                    continue

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write({
                    'state': 'exception',
                    'failure_reason': _(
                        'Error without exception. Probably due to sending an email without computed recipients.'),
                })
                # Update notification in a transient exception state to avoid concurrent
                # update in case an email bounces while sending all emails related to current
                # mail record.
                notifs = self.env['mail.notification'].search([
                    ('notification_type', '=', 'email'),
                    ('mail_mail_id', 'in', mail.ids),
                    ('notification_status', 'not in', ('sent', 'canceled'))
                ])
                if notifs:
                    notif_msg = _(
                        'Error without exception. Probably due to concurrent access update of notification records. Please see with an administrator.')
                    notifs.sudo().write({
                        'notification_status': 'exception',
                        'failure_type': 'unknown',
                        'failure_reason': notif_msg,
                    })
                    # `test_mail_bounce_during_send`, force immediate update to obtain the lock.
                    # see rev. 56596e5240ef920df14d99087451ce6f06ac6d36
                    notifs.flush_recordset(['notification_status', 'failure_type', 'failure_reason'])

                # protect against ill-formatted email_from when formataddr was used on an already formatted email
                emails_from = tools.email_split(mail.email_from)
                email_from = emails_from[0] if emails_from else mail.email_from

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                # TDE note: could be great to pre-detect missing to/cc and skip sending it
                # to go directly to failed state update
                email_list = mail._prepare_outgoing_list(
                    mail_server=mail_server or mail.mail_server_id,
                    recipients_follower_status=recipients_follower_status,
                )

                partner_cc_list = [f'{partner.name} <{partner.email}>' for partner in mail.cc_partner_ids if partner.email]

                partner_bcc_list = [f'{partner.name} <{partner.email}>' for partner in mail.bcc_partner_ids if partner.email]

                partner_default_reply_to = [f'{partner.name} <{partner.email}>' for partner in mail.rply_partner_id if partner.email]

                # send each sub-email
                for email in email_list:
                    # if given, contextualize sending using alias domains
                    if alias_domain_id:
                        alias_domain = self.env['mail.alias.domain'].sudo().browse(alias_domain_id)
                        SendIrMailServer = IrMailServer.with_context(
                            domain_notifications_email=alias_domain.default_from_email,
                            domain_bounce_address=email['headers'].get('Return-Path') or alias_domain.bounce_email,
                        )
                    else:
                        SendIrMailServer = IrMailServer
                    msg = SendIrMailServer.build_email(
                        email_from=email_from,
                        email_to=email['email_to'],
                        subject=email['subject'],
                        body=email['body'],
                        body_alternative=email['body_alternative'],
                        email_cc=email['email_cc'] + partner_cc_list,
                        reply_to=partner_default_reply_to or email['reply_to'],
                        attachments=email['attachments'],
                        message_id=email['message_id'],
                        references=email['references'],
                        object_id=email['object_id'],
                        subtype='html',
                        subtype_alternative='plain',
                        headers=email['headers'],
                        email_bcc = partner_bcc_list
                    )
                    processing_pid = email.pop("partner_id", None)
                    try:
                        res = SendIrMailServer.send_email(
                            msg, mail_server_id=mail.mail_server_id.id, smtp_session=smtp_session)
                        if processing_pid:
                            success_pids.append(processing_pid)
                        processing_pid = None
                    except AssertionError as error:
                        if str(error) == IrMailServer.NO_VALID_RECIPIENT:
                            # if we have a list of void emails for email_list -> email missing, otherwise generic email failure
                            if not email.get('email_to') and failure_type != "mail_email_invalid":
                                failure_type = "mail_email_missing"
                            else:
                                failure_type = "mail_email_invalid"
                            # No valid recipient found for this particular
                            # mail item -> ignore error to avoid blocking
                            # delivery to next recipients, if any. If this is
                            # the only recipient, the mail will show as failed.
                            _logger.info("Ignoring invalid recipients for mail.mail %s: %s",
                                         mail.message_id, email.get('email_to'))
                        else:
                            raise
                if res:  # mail has been sent at least once, no major exception occurred
                    mail.write({'state': 'sent', 'message_id': res, 'failure_reason': False})
                    _logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
                # /!\ can't use mail.state here, as mail.refresh() will cause an error
                # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                mail._postprocess_sent_message(success_pids=success_pids, failure_type=failure_type)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception(
                    'MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option',
                    mail.id, mail.message_id)
                # mail status will stay on ongoing since transaction will be rollback
                raise
            except (psycopg2.Error, smtplib.SMTPServerDisconnected):
                # If an error with the database or SMTP session occurs, chances are that the cursor
                # or SMTP session are unusable, causing further errors when trying to save the state.
                _logger.exception(
                    'Exception while processing mail with ID %r and Msg-Id %r.',
                    mail.id, mail.message_id)
                raise
            except Exception as e:
                if isinstance(e, AssertionError):
                    # Handle assert raised in IrMailServer to try to catch notably from-specific errors.
                    # Note that assert may raise several args, a generic error string then a specific
                    # message for logging in failure type
                    error_code = e.args[0]
                    if len(e.args) > 1 and error_code == IrMailServer.NO_VALID_FROM:
                        # log failing email in additional arguments message
                        failure_reason = tools.ustr(e.args[1])
                    else:
                        failure_reason = error_code
                    if error_code == IrMailServer.NO_VALID_FROM:
                        failure_type = "mail_from_invalid"
                    elif error_code in (IrMailServer.NO_FOUND_FROM, IrMailServer.NO_FOUND_SMTP_FROM):
                        failure_type = "mail_from_missing"
                # generic (unknown) error as fallback
                if not failure_reason:
                    failure_reason = tools.ustr(e)
                if not failure_type:
                    failure_type = "unknown"

                _logger.exception('failed sending mail (id: %s) due to %s', mail.id, failure_reason)
                mail.write({
                    "failure_reason": failure_reason,
                    "failure_type": failure_type,
                    "state": "exception",
                })
                mail._postprocess_sent_message(
                    success_pids=success_pids,
                    failure_reason=failure_reason, failure_type=failure_type
                )
                if raise_exception:
                    if isinstance(e, (AssertionError, UnicodeEncodeError)):
                        if isinstance(e, UnicodeEncodeError):
                            value = "Invalid text: %s" % e.object
                        else:
                            value = '. '.join(e.args)
                        raise MailDeliveryException(value)
                    raise

            if auto_commit is True:
                self._cr.commit()
        # 5/0
        return True
