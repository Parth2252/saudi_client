# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Uncanny Consulting Services LLP
#    Copyright (C) 2023 Uncanny Consulting Services LLP (<https://uncannycs.com>).
#
##############################################################################
{
    'name': "UCS Purchase Customization",
    'summary': "Add global and line-level discount functionality to Purchase Orders with accounting impact.",
    'description': """This module adds discount functionality to Purchase Orders, allowing percentage, fixed, or global discounts similar to Sales. Discounts are applied before taxes, reflected in reports and accounting, and ensure consistency with the Sales module’s workflow.""",
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','purchase','account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_order_discount_wizard_view.xml',
        'views/purchase_order_view.xml',
    ]
}

