# -*- coding: utf-8 -*-
import base64
import io
import csv
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

try:
    import xlrd
except ImportError:
    xlrd = None

try:
    import openpyxl
except ImportError:
    openpyxl = None

_logger = logging.getLogger(__name__)

class ImportInventoryWizard(models.TransientModel):
    _name = 'import.inventory.wizard'
    _description = 'Import Inventory Wizard'

    file = fields.Binary(string='File', required=True)
    file_name = fields.Char(string='File Name')
    import_option = fields.Selection([
        ('csv', 'CSV File'),
        ('excel', 'Excel File')
    ], string='Import Option', default='excel', required=True)

    def action_import_inventory(self):
        if self.import_option == 'csv':
            data = self._read_csv()
        else:
            data = self._read_excel()

        if not data:
            raise UserError(_("No data found in the file."))

        # Find column indices based on headers
        header_row = data[0]
        col_map = {
            'ts_code': -1,
            'qty': -1,
            'location': -1
        }
        
        for i, cell in enumerate(header_row):
            if not cell: continue
            cell_val = str(cell).upper().strip()
            if 'TS CODE' in cell_val:
                col_map['ts_code'] = i
            elif 'QTY' in cell_val:
                col_map['qty'] = i
            elif 'LOCATION' in cell_val:
                col_map['location'] = i

        # Fallback to defaults if headers not found correctly
        if col_map['ts_code'] == -1: col_map['ts_code'] = 1 # Column B
        if col_map['qty'] == -1: col_map['qty'] = 3     # Column D
        if col_map['location'] == -1: col_map['location'] = 4 # Column E

        log = self.env['stock.inventory.log'].create({
            'file_name': self.file_name,
            'total_records': len(data) - 1,
        })

        def _format_str(val):
            if val is None: return None
            if isinstance(val, float) and val.is_integer():
                return str(int(val))
            return str(val).strip()

        log_lines = []
        quants_to_apply = self.env['stock.quant']
        count = 0
        for row_idx, row in enumerate(data):
            if row_idx == 0: continue
            if not any(row): continue

            max_idx = max(col_map.values())
            while len(row) <= max_idx:
                row.append(None)

            internal_ref = _format_str(row[col_map['ts_code']])
            qty_raw = row[col_map['qty']]
            location_name = _format_str(row[col_map['location']])
            
            qty = 0
            try:
                if isinstance(qty_raw, str):
                    qty = float(qty_raw.strip() or 0)
                else:
                    qty = float(qty_raw) if qty_raw is not None else 0.0
            except (ValueError, TypeError):
                log_lines.append((0, 0, {
                    'row_number': row_idx + 1,
                    'ts_code': internal_ref,
                    'qty': 0,
                    'location': location_name,
                    'status': 'skipped',
                    'reason': _("Invalid quantity '%s'") % qty_raw
                }))
                continue

            # Validations
            skip_reason = False
            product = False
            location = False

            if not internal_ref:
                skip_reason = _("TS CODE is missing")
            elif not location_name:
                skip_reason = _("Location is missing")
            else:
                product = self.env['product.product'].search([('default_code', '=', internal_ref)], limit=1)
                if not product:
                    skip_reason = _("Product '%s' not found") % internal_ref
                elif not product.is_storable:
                    skip_reason = _("Product '%s' is not storable") % internal_ref
                else:
                    location = self.env['stock.location'].search([
                        '|', ('complete_name', 'ilike', location_name), ('name', 'ilike', location_name),
                        ('usage', '=', 'internal')
                    ], limit=1)
                    if not location:
                        skip_reason = _("Location '%s' not found") % location_name

            if skip_reason:
                log_lines.append((0, 0, {
                    'row_number': row_idx + 1,
                    'ts_code': internal_ref,
                    'qty': qty,
                    'location': location_name,
                    'status': 'skipped',
                    'reason': skip_reason
                }))
                continue

            # Update stock.quant
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id', '=', location.id),
                ('lot_id', '=', False),
                ('package_id', '=', False),
                ('owner_id', '=', False)
            ], limit=1)

            if not quant:
                quant = self.env['stock.quant'].create({
                    'product_id': product.id,
                    'location_id': location.id,
                    'inventory_quantity': qty,
                })
            else:
                quant.inventory_quantity = qty
            
            quants_to_apply |= quant
            count += 1
            log_lines.append((0, 0, {
                'row_number': row_idx + 1,
                'ts_code': internal_ref,
                'qty': qty,
                'location': location.complete_name,
                'status': 'success',
            }))

        if quants_to_apply:
            quants_to_apply.with_context(inventory_mode=True).action_apply_inventory()

        log.write({
            'imported_records': count,
            'skipped_records': (len(log_lines) - count),
            'line_ids': log_lines
        })

        return {
            'name': _('Import Result'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.inventory.log',
            'view_mode': 'form',
            'res_id': log.id,
            'target': 'current',
        }

    def _read_csv(self):
        try:
            content = base64.b64decode(self.file)
            # Try different encodings
            try:
                decoded_content = content.decode('utf-8')
            except UnicodeDecodeError:
                decoded_content = content.decode('latin1')
            
            reader = csv.reader(io.StringIO(decoded_content), delimiter=',', quotechar='"')
            return list(reader)
        except Exception as e:
            raise UserError(_("Error reading CSV file: %s") % str(e))

    def _read_excel(self):
        content = base64.b64decode(self.file)
        if self.file_name and self.file_name.endswith('.xlsx'):
            if not openpyxl:
                raise UserError(_("The 'openpyxl' library is required to read .xlsx files."))
            try:
                wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
                sheet = wb.active
                data = []
                for row in sheet.iter_rows(values_only=True):
                    data.append(list(row))
                return data
            except Exception as e:
                raise UserError(_("Error reading XLSX file: %s") % str(e))
        else:
            if not xlrd:
                raise UserError(_("The 'xlrd' library is required to read .xls files."))
            try:
                workbook = xlrd.open_workbook(file_contents=content)
                sheet = workbook.sheet_by_index(0)
                data = []
                for row_idx in range(sheet.nrows):
                    row = []
                    for col_idx in range(sheet.ncols):
                        row.append(sheet.cell_value(row_idx, col_idx))
                    data.append(row)
                return data
            except Exception as e:
                raise UserError(_("Error reading XLS file: %s") % str(e))

