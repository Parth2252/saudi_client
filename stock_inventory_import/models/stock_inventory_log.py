# -*- coding: utf-8 -*-
from odoo import models, fields

class StockInventoryLog(models.Model):
    _name = 'stock.inventory.log'
    _description = 'Stock Inventory Import Log'
    _order = 'create_date desc'

    import_date = fields.Datetime(string='Import Date', default=fields.Datetime.now)
    file_name = fields.Char(string='File Name')
    total_records = fields.Integer(string='Total Records')
    imported_records = fields.Integer(string='Imported Records')
    skipped_records = fields.Integer(string='Skipped Records')
    line_ids = fields.One2many('stock.inventory.log.line', 'log_id', string='Log Lines')

class StockInventoryLogLine(models.Model):
    _name = 'stock.inventory.log.line'
    _description = 'Stock Inventory Import Log Line'

    log_id = fields.Many2one('stock.inventory.log', string='Log', ondelete='cascade')
    row_number = fields.Integer(string='Row Number')
    ts_code = fields.Char(string='TS Code')
    qty = fields.Float(string='Quantity')
    location = fields.Char(string='Location')
    status = fields.Selection([
        ('success', 'Success'),
        ('skipped', 'Skipped')
    ], string='Status')
    reason = fields.Text(string='Reason/Error')
