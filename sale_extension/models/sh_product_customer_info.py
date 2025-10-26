from odoo import models, fields, api


class ShProductCustomerInfo(models.Model):
    _inherit = "sh.product.customer.info"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'product_name' in vals and vals.get('product_name'):
                vals['product_name'] = str(vals['product_name']).upper()
        res = super(ShProductCustomerInfo, self).create(vals_list)
        return res

    def write(self, vals):
        if 'product_name' in vals and vals['product_name']:
            vals['product_name'] = str(vals['product_name'].upper())
        res = super(ShProductCustomerInfo, self).write(vals)
        return res

    def update_old_product_sh_record_to_uppercase(self):
        for record in self:
            if record.product_name:
                record.product_name = record.product_name.upper()


