# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'All in One Import Order Lines | Import Sales Order Line | Import Purchase Order Line | Import Invoice Line',
    'version': '18.0.0.0',
    'category': 'Extra Tools',
    'summary': 'All Import order lines all in one import order lines import sales order line import purchase order line import invoice line import vendor bill line all in one import orders line all import line import quotation line import RFQ line import sale line imports',
    "description": """

       All in One Import Order Lines in odoo,
       Import Sale Order Lines in odoo,
       Import Purchase Order Lines in odoo,
       Import Invoice Lines in odoo,
       Import CSV File in odoo,
       Import XLS File in odoo,
       Import Product Details in odoo,
    
    """,
    'author': 'BROWSEINFO',
    "price": 19,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.com/demo-request?app=bi_import_all_orders_lines&version=18&edition=Community',
    'depends': ['base','sale_management','purchase','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/import_order_lines_view.xml',
        'data/sales_attachment_sample.xml',
        'views/import_po_lines_view.xml',
        'data/purchase_attachment_sample.xml',
        'wizard/import_invoice_lines_view.xml',
        'data/invoice_attachment_sample.xml',
            ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://www.browseinfo.com/demo-request?app=bi_import_all_orders_lines&version=18&edition=Community',
    "images": ['static/description/Banner.gif'],
}

