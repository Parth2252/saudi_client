from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    datasheet_attach = fields.Boolean(string='Datasheet Attach')
    upload_datasheet_attachment = fields.Binary(string='Upload Datasheet')

    def is_attachment_image(self):
        if not self.upload_datasheet_attachment:
            return False
        import base64
        try:
            decoded = base64.b64decode(self.upload_datasheet_attachment)
            # Check for common image headers: JPEG, PNG, GIF
            return decoded.startswith(b'\xff\xd8') or decoded.startswith(b'\x89PNG') or decoded.startswith(b'GIF8')
        except:
            return False

    def is_attachment_pdf(self):
        if not self.upload_datasheet_attachment:
            return False
        import base64
        try:
            decoded = base64.b64decode(self.upload_datasheet_attachment)
            return decoded.startswith(b'%PDF')
        except:
            return False

    def _prepare_procurement_values(self, group_id):
        """Inject datasheet_attach into procurement values."""
        res = super()._prepare_procurement_values(group_id)
        res.update({
            'datasheet_attach': self.datasheet_attach,
        })
        return res



