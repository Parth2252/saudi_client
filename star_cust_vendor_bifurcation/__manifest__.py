# -*- coding: utf-8 -*-
# Part of The Stella Technolabs. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer Vendor Bifurcation',
    'version': '18.0.1.0.1',
    'summary': 'The module introduces a user-friendly checkbox feature for easy categorization of records into customer and vendor segments, streamlining data management and enhancing user experience.',
    'description': '''
        Customer filter
        Vendor filter
        customer vendor checkbox
        cust vendor
        custvendor
    ''',
    'category': 'Sales/CRM',
    'depends': ['base','sale','contacts','account'],
    'data': [
        'data/sequence.xml',
        'data/ir_cron.xml',
        'views/res_config_settings.xml',
        'views/views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    # 'price': 9.00,
    # 'currency': 'EUR',
}
