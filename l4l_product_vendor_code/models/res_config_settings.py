# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################


from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_vendor_code_and_name = fields.Boolean(string="Add/Update Product Code From Purchase Order", default=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_vendor_code_and_name = fields.Boolean(related='company_id.enable_vendor_code_and_name', readonly=False)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
