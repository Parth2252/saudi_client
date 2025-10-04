# -*- coding: utf-8 -*-
{
    # Application Information
    'name': "Order Report Merge",
    'summary': "This module helps to add multiple pdfs in sale order and merge with quotation to print",
    'category': 'Human Resources',
    'version': '18.0.0.1',

    # Author Information
    'author': "v",
    'website': "test.com",
    'license': "AGPL-3",

    # Technical Information
    'depends': ['base', 'sale_management', 'sale_extension','sale'],

    'data': [
        'views/sale_order.xml',
    ],

    # App Technical Information
    'installable': True,
    'auto_install': False,
    'application': False

}
