from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    datasheet_attach = fields.Boolean(string='Datasheet Attach')

    def _prepare_procurement_values(self, group_id):
        """Inject datasheet_attach into procurement values."""
        res = super()._prepare_procurement_values(group_id)
        res.update({
            'datasheet_attach': self.datasheet_attach,
        })
        return res



