# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    vendor_product_name = fields.Char(string='Vendor Product Name')
    vendor_product_code = fields.Char(string='Vendor Product Code')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
