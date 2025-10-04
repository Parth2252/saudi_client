# -*- coding: utf-8 -*-
{
    'name': "Custom Report",
    'version': '18.0',
    'summary': 'Custom report',
    'sequence': 10,
    'description': """
Custom Report
    """,
    'category': 'Custom',
    'website': 'vighnesh@gmail.com',
    'depends': ['purchase', 'mail', 'sale','sh_product_customer_code'],
    'data': [
        'data/pur_email_temp.xml',
        'data/sale_email_temp.xml',
        # 'views/purchase_order.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,

    'license': 'OPL-1',
}
