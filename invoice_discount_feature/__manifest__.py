# -*- coding: utf-8 -*-
{
    'name': "Invoice Discount Feature",
    'summary': """This module adds discount functionality to Customer and Vendor Invoices (`account.move`), allowing percentage, fixed, or global discounts. Discounts are applied before taxes, properly reflected in reports, journal entries, and accounting records. It ensures consistency with the Sales module’s discount workflow and maintains accurate financial reporting.""",
    'description': """This module adds discount functionality to Customer and Vendor Invoices (`account.move`), allowing percentage, fixed, or global discounts. Discounts are applied before taxes, properly reflected in reports, journal entries, and accounting records. It ensures consistency with the Sales module’s discount workflow and maintains accurate financial reporting.""",
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Invoices',
    'version': '0.1',
    'depends': ['base','account','product','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_move_discount_wizard_view.xml',
        'views/account_move_view.xml',
    ]
}



