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
        "security/ir.model.access.csv",
        "security/security.xml",
        "wizard/purchase_source_wizard_view.xml",
        'report/purchase_quotation_report.xml',
        'report/purchase_report.xml',
        'views/purchase_order.xml',
        'views/product.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'purchase_extension/static/src/views/purchase_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
