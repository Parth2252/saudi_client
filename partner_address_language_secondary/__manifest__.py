# -*- coding: utf-8 -*-

{
    'name': 'Customer Dual Language',
    'version': '1.0',
    'summary': """Secondary language in the partner/customer/supplier form. Like address in arabic/Saudi/KSA/Dubai/Spanish/Chinese/Dutch/Greek/Russian/Hindi/French/Japanese/German/Portuguese/Korean/Italian/Turkish/Persian .  Translate/Translation """,
    'description': """Secondary language in the partner/customer/supplier form. Like address in arabic/Saudi/KSA/Dubai/Spanish/Chinese/Dutch/Greek/Russian/Hindi/French/Japanese/German/Portuguese/Korean/Italian/Turkish/Persian. Translate/Translation """,
    'category': 'Base',
    'author': 'bisolv',
    'website': "",
    'license': 'AGPL-3',

    'price': 0,
    'currency': 'USD',

    'depends': ['base_setup', 'product', 'account'],

    'data': [
        'views/res_config_settings_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/product_template_view.xml'
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}
