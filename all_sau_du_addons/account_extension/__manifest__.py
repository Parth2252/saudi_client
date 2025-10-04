# -*- coding: utf-8 -*-
{
    'name': "Account Extended",
    'version': '18.0',
    'summary': 'Account New',
    'sequence': 10,
    'description': """
Account Extended
    """,
    'category': 'Custom',
    'depends': ['base','account','sale_extension'],
    'data': [
        'data/ir_sequence.xml',
        'views/account_move.xml',
    ],
    'demo': [
    ],

    'installable': True,
    'application': True,

    'license': 'OPL-1',
}
