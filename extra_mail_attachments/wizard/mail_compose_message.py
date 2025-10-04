# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    extra_attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="mail_compose_ir_attachment_rel",
        string="Extra Attachments",
        default=lambda self: self._get_auto_attachments(),
    )

    has_extra_attachments = fields.Boolean(compute='_compute_has_extra_attachments')

    def _get_auto_attachments(self):
        """
        Method For getting attachments of individual
        records automatically in mail wizard
        """
        default_res_id = self._context.get("default_res_ids")
        default_model = self._context.get("default_model")
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", default_res_id), ("res_model", "=", default_model)]
        )
        return attachments

    @api.depends('extra_attachment_ids')
    def _compute_has_extra_attachments(self):
        for record in self:
            record.has_extra_attachments = bool(record.extra_attachment_ids)
