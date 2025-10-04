from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    datasheet_attach = fields.Boolean(string='Datasheet Attach')

    @api.model
    def create(self, vals):
        # Check if procurement origin exists and has the flag
        if vals.get('sale_line_id'):
            sale_line = self.env['sale.order.line'].browse(vals['sale_line_id'])
            vals['datasheet_attach'] = sale_line.datasheet_attach
        return super().create(vals)


