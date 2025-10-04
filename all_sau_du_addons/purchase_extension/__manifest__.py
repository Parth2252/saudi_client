# -*- coding: utf-8 -*-
{
    'name': "Purchase Extended",
    'version': '18.0',
    'summary': 'Purchase New',
    'sequence': 10,
    'description': """
Purchase Extended
    """,
    'category': 'Custom',
    'depends': ['product','purchase', 'sale_purchase_stock','purchase_stock','account', 'crm'],
    'data': [
        "security/security.xml",
        'report/purchase_quotation_report.xml',
        'report/purchase_report.xml',
        'views/purchase_order.xml',
        'views/product.xml',
    ],
    'demo': [
    ],

    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
