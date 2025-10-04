# -*- coding: utf-8 -*-
{
    'name': "QR",
    'version': '18.0',
    'summary': 'QR Code & Rep',
    'sequence': 10,
    'description': """
QR
    """,
    'category': 'Custom',
    'website': 'self@gmail.com',
    'depends': ['stock', 'mail', 'sale', 'sale_extension', 'purchase_extension', 'sh_product_customer_code'],
    'data': [
        # 'data/pur_email_temp.xml',
        # 'data/sale_email_temp.xml',
        'security/ir.model.access.csv',
        'report/delivery_slip_report.xml',
        'report/delivery_paper_format.xml',

        'views/stock_picking.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,

    'license': 'OPL-1',
}
