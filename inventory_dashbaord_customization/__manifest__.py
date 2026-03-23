# -*- coding: utf-8 -*-
{
    'name': "Inventory Dashboard Customization",
    'version': '18.0',
    'summary': 'Custom Inventory Dashboard for Receipts and Deliveries',
    'sequence': 10,
    'description': """
Inventory Dashboard Customization
    """,
    'category': 'Custom',
    'depends': ['stock', 'purchase_stock', 'sale_stock'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'inventory_dashbaord_customization/static/src/views/inventory_dashboard.js',
            'inventory_dashbaord_customization/static/src/views/inventory_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
