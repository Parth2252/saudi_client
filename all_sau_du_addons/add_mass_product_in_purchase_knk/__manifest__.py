# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Add/import  Mass/multiple product in purchase',
    'version': '18.0.1.2',
    'category': 'Inventory/Purchase',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'summary': '''
        This module is allow to add multiple product in purchase order line or import order line from xlsx file and xls file
        Add multiple products in purchase order line | Import purchase order line from xlsx file|Download sample file | Import purchase order line from xls file | select multiple product
    ''',
    'description': '''
        You can select multiple product from 'Add mass product' button
        You can able to import purchase order line by xlsx file
        You can able to import purchase order line by xls file
        You can Sample file download from sample.xlsx
        You can Sample file download from sample.xls
    ''',
    'depends': [
        'purchase'
    ],
    'data': [
        'wizard/add_mass_product_wizard_view.xml',
        'wizard/import_from_file_wizard_view.xml',
        'views/purchase_order_views.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'currency': 'EUR',
    'price': 20
}
