# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, exceptions
from datetime import datetime
import binascii
import tempfile
from tempfile import TemporaryFile
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import io

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class import_invoice_wizard(models.TransientModel):
    _name='import.invoice.wizard'
    _description='import invoice wizard'

    invoice_file = fields.Binary(string="Select File")
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='File Format',default='csv')
    import_prod_option = fields.Selection([('barcode', 'Barcode'),('code', 'Code'),('name', 'Name')],string='Import Product By ',default='name')
    product_details_option = fields.Selection([('from_product','Take Details From The Product'),('from_xls','Take Details From The XLS File')],default='from_xls')
    import_analytic_account_tags = fields.Boolean("Import Analytic Account & Tags")
    
    sample_option = fields.Selection([('csv', 'CSV'),('xls', 'XLS')],string='Sample Type',default='csv')
    down_samp_file = fields.Boolean(string='Download Sample Files')
    
    
    def import_inv(self):
        if self.import_option == 'csv':
            if self.import_analytic_account_tags == True:
                keys = ['product', 'quantity', 'uom','description', 'price', 'tax','analytic_account','analytic_tags']
                try:
                    csv_data = base64.b64decode(self.invoice_file)
                    data_file = io.StringIO(csv_data.decode("utf-8"))
                    data_file.seek(0)
                    file_reader = []
                    csv_reader = csv.reader(data_file, delimiter=',')
                    file_reader.extend(csv_reader)
                except Exception:
                    raise exceptions.ValidationError(_("Invalid file!"))
                values = {}
                for i in range(len(file_reader)):
                    field = list(map(str, file_reader[i]))
                    values = dict(zip(keys, field))
                    if values:
                        if i == 0:
                            continue
                        else:
                            res = self.create_inv_line(values)
            else:
                keys = ['product', 'quantity', 'uom','description', 'price', 'tax']
                try:
                    csv_data = base64.b64decode(self.invoice_file)
                    data_file = io.StringIO(csv_data.decode("utf-8"))
                    data_file.seek(0)
                    file_reader = []
                    csv_reader = csv.reader(data_file, delimiter=',')
                    file_reader.extend(csv_reader)
                except Exception:
                    raise exceptions.ValidationError(_("Invalid file!"))
                values = {}
                for i in range(len(file_reader)):
                    field = list(map(str, file_reader[i]))
                    values = dict(zip(keys, field))
                    if values:
                        if i == 0:
                            continue
                        else:
                            res = self.create_inv_line(values)
        else:
            if self.import_analytic_account_tags == True:
                try:
                    fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    fp.write(binascii.a2b_base64(self.invoice_file))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)
                except Exception:
                    raise exceptions.ValidationError(_("Invalid file!"))
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                        if self.product_details_option == 'from_product':
                                                values.update({
                                                'product' : line[0].split('.')[0],
                                                'quantity' : line[1],
                                                # 'analytic_distribution' : line[6],
                                                # 'analytic_tags' : line[7]

                                            })
                        else:
                            values.update({
                                    'product':line[0].split('.')[0],
                                    'quantity':line[1],
                                    'uom':line[2],
                                    'description':line[3],
                                    'price':line[4],
                                    'tax':line[5],
                                    # 'analytic_distribution' : line[6],
                                    # 'analytic_tags' : line[7]
                                })
                        res = self.create_inv_line(values)
            else:
                try:
                    fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    fp.write(binascii.a2b_base64(self.invoice_file))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)
                except Exception:
                    raise exceptions.ValidationError(_("Invalid file!"))
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                        if self.product_details_option == 'from_product':
                                                values.update({
                                                'product' : line[0].split('.')[0],
                                                'quantity' : line[1],
                                            })
                        else:
                            values.update({
                                    'product':line[0].split('.')[0],
                                    'quantity':line[1],
                                    'uom':line[2],
                                    'description':line[3],
                                    'price':line[4],
                                    'tax':line[5],
                                })
                        res = self.create_inv_line(values)
        return res

    def create_inv_line(self,values):
        analytic_account_search = False
        account_inv_brw=self.env['account.move'].browse(self._context.get('active_id'))
        product=values.get('product')
        if self.product_details_option == 'from_product':
            if self.import_prod_option == 'barcode':
                product_obj_search=self.env['product.product'].search([('barcode',  '=',values['product'])])
            elif self.import_prod_option == 'code':
                product_obj_search=self.env['product.product'].search([('default_code', '=',values['product'])])
            else:
                product_obj_search=self.env['product.product'].search([('name', '=',values['product'])])
            if product_obj_search:
                product_id=product_obj_search
            else:
                raise ValidationError(_('%s product is not found".') % values.get('product'))

            if self.import_analytic_account_tags == True:
                analytic_account_search = False
                if values.get('analytic_distribution') :
                    analytic_account_search = self.env['account.analytic.account'].search([('name','=',values.get('analytic_account') )],limit=1)
                    if not analytic_account_search :
                        raise ValidationError(_('%s Analytic Account is not found".') % values.get('analytic_account'))

                tag_id_lst = []
                if values.get('analytic_tags') :
                    if ';' in  values.get('analytic_tags'):
                        analytic_tags_names = values.get('analytic_tags').split(';')
                        for name in analytic_tags_names:
                            tag= self.env['account.analytic.plan'].search([('name', '=', name)])
                            if not tag:
                                raise ValidationError(_('"%s" Tag not in your system') % name)
                            tag_id_lst.append(tag.id)
                    elif ',' in  values.get('analytic_tags'):
                        analytic_tags_names = values.get('analytic_tags').split(',')
                        for name in analytic_tags_names:
                            tag= self.env['account.analytic.plan'].search([('name', '=', name)])
                            if not tag:
                                raise ValidationError(_('"%s" Tag not in your system') % name)
                            tag_id_lst.append(tag.id)
                    else:
                        analytic_tags_names = values.get('analytic_tags').split(',')
                        tag= self.env['account.analytic.plan'].search([('name', '=', analytic_tags_names)])
                        if not tag:
                            raise ValidationError(_('"%s" Tag not in your system') % analytic_tags_names)
                        tag_id_lst.append(tag.id)        

                    if not tag_id_lst :
                        raise ValidationError(_('%s Analytic Tag is not found".') % values.get('analytic_tags'))

            if account_inv_brw.move_type == "out_invoice" and account_inv_brw.state == 'draft':
                cust_account_id = product_id.property_account_income_id.id
                if cust_account_id:
                    account_id = cust_account_id
                else:
                    account_id = product_id.categ_id.property_account_income_categ_id.id
                    if analytic_account_search:
                        analytic_account_id = analytic_account_search.id
                    else:
                        analytic_account_id = False
                    if self.import_analytic_account_tags == True:
                
                        vals = {
                                'account_id':account_id,
                                'product_id':product_id.id,
                                'name':product_id.name,
                                'quantity':values.get('quantity'),
                                'product_uom_id':product_id.uom_id.id,
                                'price_unit':product_id.lst_price,
                                # 'analytic_distribution' : analytic_distribution,
                                # 'analytic_tag_ids' : [(6,0,tag_id_lst)],
                                # 'analytic_distribution': self.analytic_distribution,
                                }
                        account_inv_brw.write({'invoice_line_ids' : ([(0,0,vals)]) } )    
                        return True
                    else:
                        vals = {
                                'account_id':account_id,
                                'product_id':product_id.id,
                                'name':product_id.name,
                                'quantity':values.get('quantity'),
                                'product_uom_id':product_id.uom_id.id,
                                'price_unit':product_id.lst_price,
                                }
                        account_inv_brw.write({'invoice_line_ids' : ([(0,0,vals)]) } )

            elif account_inv_brw.move_type =="in_invoice" and account_inv_brw.state == 'draft':
                vendor_account_id = product_id.property_account_expense_id.id
                if vendor_account_id:
                    account_id = vendor_account_id
                else:
                    account_id = product_id.categ_id.property_account_expense_categ_id.id
                if analytic_account_search:
                    analytic_account_id = analytic_account_search.id
                else:
                    analytic_account_id = False
                if self.import_analytic_account_tags == True:    
                    vals = {
                            'account_id':account_id,
                            'product_id':product_id.id,
                            'name':product_id.name,
                            'quantity':values.get('quantity'),
                            'product_uom_id':product_id.uom_id.id,
                            'price_unit':product_id.lst_price,
                            # 'analytic_account_id' : analytic_account_id,
                            # 'analytic_tag_ids' : [(6,0,tag_id_lst)]
                            }
                    account_inv_brw.write({'invoice_line_ids' : ([(0,0,vals)])  }   )    
                    return True
                else:
                    vals = {
                        'account_id':account_id,
                        'product_id':product_id.id,
                        'name':product_id.name,
                        'quantity':values.get('quantity'),
                        'product_uom_id':product_id.uom_id.id,
                        'price_unit':product_id.lst_price,
                        }
                    account_inv_brw.write({'invoice_line_ids' : ([(0,0,vals)])  }   )    
                    return True
            
            elif account_inv_brw.state != 'draft':
                raise UserError(_('We cannot import data in validated or confirmed Invoice.')) 

        else:
            uom=values.get('uom')
            if self.import_prod_option == 'barcode':
                product_obj_search=self.env['product.product'].search([('barcode',  '=',values['product'])])
            elif self.import_prod_option == 'code':
                product_obj_search=self.env['product.product'].search([('default_code', '=',values['product'])])
            else:
                product_obj_search=self.env['product.product'].search([('name', '=',values['product'])])
            
            uom_obj_search=self.env['uom.uom'].search([('name','=',uom)])
            if not uom_obj_search:
                raise ValidationError(_('UOM "%s" is Not Available') % uom)

            if self.import_analytic_account_tags == True:
                analytic_account_search = False
                if values.get('analytic_account') :
                    analytic_account_search = self.env['account.analytic.account'].search([('name','=',values.get('analytic_account') )],limit=1)
                    if not analytic_account_search :
                        raise ValidationError(_('%s Analytic Account is not found".') % values.get('analytic_account'))

                tag_id_lst = []
                if values.get('analytic_tags') :
                    if ';' in  values.get('analytic_tags'):
                        analytic_tags_names = values.get('analytic_tags').split(';')
                        for name in analytic_tags_names:
                            tag= self.env['account.analytic.tag'].search([('name', '=', name)])
                            if not tag:
                                raise ValidationError(_('"%s" Tag not in your system') % name)
                            tag_id_lst.append(tag.id)
                    elif ',' in  values.get('analytic_tags'):
                        analytic_tags_names = values.get('analytic_tags').split(',')
                        for name in analytic_tags_names:
                            tag= self.env['account.analytic.plan'].search([('name', '=', name)])
                            if not tag:
                                raise ValidationError(_('"%s" Tag not in your system') % name)
                            tag_id_lst.append(tag.id)
                    else:
                        analytic_tags_names = values.get('analytic_tags')
                        tag= self.env['account.analytic.plan'].search([('name', '=', analytic_tags_names)])
                        if not tag:
                            raise ValidationError(_('"%s" Tag not in your system') % analytic_tags_names)
                        tag_id_lst.append(tag.id)        

                    if not tag_id_lst :
                        raise ValidationError(_('%s Analytic Tag is not found".') % values.get('analytic_tags'))

            if product_obj_search:
                product_id=product_obj_search
            else:
                if self.import_prod_option == 'name':
                    product_id=self.env['product.product'].create({'name':product,'lst_price':values.get('price')})
                else:
                    raise ValidationError(_('%s product is not found" .\n If you want to create product then first select Import Product By Name option .') % values.get('product'))

            if account_inv_brw.move_type == "out_invoice" and account_inv_brw.state == 'draft':
                tax_id_lst=[]
                if values.get('tax'):
                    if ';' in  values.get('tax'):
                        tax_names = values.get('tax').split(';')
                        for name in tax_names:
                            tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
                            if not tax:
                                raise ValidationError(_('"%s" Tax not in your system') % name)
                            tax_id_lst.append(tax.id)
                    elif ',' in  values.get('tax'):
                        tax_names = values.get('tax').split(',')
                        for name in tax_names:
                            tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
                            if not tax:
                                raise ValidationError(_('"%s" Tax not in your system') % name)
                            tax_id_lst.append(tax.id)
                    else:
                        tax_names = values.get('tax').split(',')
                        tax= self.env['account.tax'].search([('name', '=', tax_names),('type_tax_use','=','sale')])
                        if not tax:
                            raise ValidationError(_('"%s" Tax not in your system') % tax_names)
                        tax_id_lst.append(tax.id)

                cust_account_id = product_id.property_account_income_id.id
                if cust_account_id:
                    account_id = cust_account_id
                else:
                    account_id = product_id.categ_id.property_account_income_categ_id.id

                if analytic_account_search:
                    analytic_account_id = analytic_account_search.id
                else:
                    analytic_account_id = False
                if self.import_analytic_account_tags == True:
                    vals ={
                            'account_id':account_id,
                            'product_id':product_id.id,
                            'name':values.get('description'),
                            'quantity':values.get('quantity'),
                            'product_uom_id':uom_obj_search.id,
                            'price_unit':values.get('price'),
                            # 'analytic_account_id' : analytic_account_id,
                            # 'analytic_tag_ids' : [(6,0,tag_id_lst)],
                            'tax_ids':([(6,0,tax_id_lst)])
                            }
                    account_inv_brw.write({'invoice_line_ids' : ([(0,0,vals)])  }   )    
                    return True
                else:
                    vals ={
                        'account_id':account_id,
                        'product_id':product_id.id,
                        'name':values.get('description'),
                        'quantity':values.get('quantity'),
                        'product_uom_id':uom_obj_search.id,
                        'price_unit':values.get('price'),
                        'tax_ids':([(6,0,tax_id_lst)])
                        }
                    account_inv_brw.write({'invoice_line_ids' : ([(0,0,vals)])  }   )    
                    return True

            elif account_inv_brw.move_type =="in_invoice" and account_inv_brw.state == 'draft':
                tax_id_lst=[]
                if values.get('tax'):
                    if ';' in  values.get('tax'):
                        tax_names = values.get('tax').split(';')
                        for name in tax_names:
                            tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','purchase')])
                            if not tax:
                                raise ValidationError(_('"%s" Tax not in your system') % name)
                            tax_id_lst.append(tax.id)
                    elif ',' in  values.get('tax'):
                        tax_names = values.get('tax').split(',')
                        for name in tax_names:
                            tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','purchase')])
                            if not tax:
                                raise ValidationError(_('"%s" Tax not in your system') % name)
                            tax_id_lst.append(tax.id)
                    else:
                        tax_names = values.get('tax').split(',')
                        tax= self.env['account.tax'].search([('name', '=', tax_names),('type_tax_use','=','purchase')])
                        if not tax:
                            raise ValidationError(_('"%s" Tax not in your system') % tax_names)
                        tax_id_lst.append(tax.id)
                        
                vendor_account_id = product_id.property_account_expense_id.id
                if vendor_account_id:
                    account_id = vendor_account_id
                else:
                    account_id = product_id.categ_id.property_account_expense_categ_id.id

                if analytic_account_search:
                    analytic_account_id = analytic_account_search.id
                else:
                    analytic_account_id = False
                if self.import_analytic_account_tags == True:
                    vals = {
                            'account_id':account_id,
                            'product_id':product_id.id,
                            'name':values.get('description'),
                            'quantity':values.get('quantity'),
                            'product_uom_id':uom_obj_search.id,
                            'price_unit':values.get('price'),
                            # 'analytic_distribution' : analytic_distribution,
                            # 'analytic_tag_ids' : [(6,0,tag_id_lst)],
                            'tax_ids':([(6,0,tax_id_lst)])
                                                        }

                    account_inv_brw.write({'invoice_line_ids' : ([(0,0,vals)])  }   )    
                    return True
                else:
                    vals = {
                        'account_id':account_id,
                        'product_id':product_id.id,
                        'name':values.get('description'),
                        'quantity':values.get('quantity'),
                        'product_uom_id':uom_obj_search.id,
                        'price_unit':values.get('price'),
                        'tax_ids':([(6,0,tax_id_lst)])
                        }

                    account_inv_brw.write({'invoice_line_ids' : ([(0,0,vals)])  }   )    
                    return True
        
            elif account_inv_brw.state != 'draft':
                raise UserError(_('We cannot import data in validated or confirmed Invoice.'))
            
            
    def download_auto(self):
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_document?model=import.invoice.wizard&id=%s'%(self.id),
             'target': 'new',
             }
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: