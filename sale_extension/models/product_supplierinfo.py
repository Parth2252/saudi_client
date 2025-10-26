from odoo import models, fields, api


class Product_Supplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'product_name' in vals and vals.get('product_name'):
                vals['product_name'] = str(vals['product_name']).upper()
        res = super(Product_Supplierinfo, self).create(vals_list)
        return res

    def write(self, vals):
        if 'product_name' in vals and vals['product_name']:
            vals['product_name'] = str(vals['product_name'].upper())
        res = super(Product_Supplierinfo, self).write(vals)
        return res

    def update_old_vendor_product_name_to_uppercase(self):
        for record in self:
            if record.product_name:
                record.product_name = record.product_name.upper()


