# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Auto Generate Customer Sequence based on Prefix | Vendor Reference based on Prefix | Unique Code for Customer/Vendor',
    'version': '18.0.0.0',
    'category': 'Sales',
    'summary': 'Prefix based customer sequence Unique partner reference number generate partner sequence Prefix based vendor sequence Set custom prefix for customer codes auto assign customer number with prefix customer unique ID number vendor unique code based on prefix',
    'description': '''Auto Generate Customer Sequence based on Prefix Odoo App streamlines customer and vendor management by automatically assigning unique reference codes based on predefined prefixes. This ensures a structured and consistent identification system for customers and vendors. User can define specific prefixes for customer and vendor, allowing for easy differentiation and systematic record-keeping. This solution enhances accuracy in financial transactions, invoicing, and reporting by eliminating duplicate or inconsistent entries. User can also search specific customer or vendor wish custom sequence in POS as well.''',
    'price': 25,
    'currency': "EUR",
    'author': 'BROWSEINFO',
    'website': 'https://www.browseinfo.com/demo-request?app=bi_custmor_vendor_unquie_code&version=18&edition=Community',
    'depends': ['contacts','account',],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
    ],
    "license":'OPL-1',
    'installable': True,
    'auto_install': False,
    "live_test_url" : 'https://www.browseinfo.com/demo-request?app=bi_custmor_vendor_unquie_code&version=18&edition=Community',
    "images":['static/description/Banner.gif'],
}
