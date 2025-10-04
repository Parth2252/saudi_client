# -*- coding: utf-8 -*-
{
    'name': "crm customization",
    'summary': "Automatic update the crm stages based on purchase to delivered goods to customer workflow",
    'category': 'Crm',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'sale'],

    # always loaded
    'data': [
        'views/crm_stage_view.xml',
        'views/purchase_order_view.xml',
        'views/account_move.xml',
        'views/stock_picking_view.xml',
    ],
}


