# See LICENSE file for full copyright and licensing details.

from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def action_add_attchment(self):
        """
        Button method which will send attachment
        to default m2m field at mail wizard level.
        """
        wizard_id = self._context.get("mail_compose_wizard_id")
        wizard_model = self._context.get("mail_compose_wizard_model")
        wizard = self.env[wizard_model].browse(wizard_id)
        attachment_obj = self.env["ir.attachment"]

        for attach in self:
            attachment_id = attachment_obj.create(
                {
                    "name": attach.name,
                    "type": "binary",
                    "datas": attach.datas,
                    "res_model": wizard_model,
                    "res_id": wizard_id,
                }
            )
            wizard.attachment_ids = [(4, attachment_id.id)]
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": wizard_model,
            "views": [(False, "form")],
            "res_id": wizard_id,
            "view_id": False,
            "target": "new",
        }
