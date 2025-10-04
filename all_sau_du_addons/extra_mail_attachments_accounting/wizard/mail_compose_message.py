# See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.osv import expression


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    def _get_auto_attachments(self):
        """
        Inherit Method For getting project attachments if any linked with so
        automatically in mail wizard
        """
        attachments_ids = super()._get_auto_attachments()

        default_res_ids = self._context.get("active_id")
        default_model = self._context.get("active_model")

        if (default_model or default_res_ids) is None:
            return

        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", default_res_ids), ("res_model", "=", default_model)]
        )
        return attachments | attachments_ids
