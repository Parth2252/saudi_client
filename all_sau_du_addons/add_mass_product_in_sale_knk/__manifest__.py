# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
{
    'name': 'Add/import Mass/multiple product in order line',
    'version': '18.0.1.1',
    'license': 'OPL-1',
    'category': 'Sales/Sales',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://kanakinfosystems.com',
    'summary': '''
        This module is allow to add multiple product in sale order line or import order line from xlsx file. | Add Multiple Products In Order Lines | Import Order Lines From xlsx File | Download Sample File | Select Multiple Product
    ''',
    'description': '''
        You can select multiple product from 'Add mass product' button
        You can able to import order lines by xlsx file
        You can Sample file download from sample.xlsx
    ''',
    'depends': [
        'sale_management'
    ],
    'data': [
        'wizard/add_mass_product_wizard_view.xml',
        'wizard/import_from_file_wizard_view.xml',
        'views/knk_sale_order_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'currency': 'EUR',
    'price': 20
}
