# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Advance Down Payment for Sales and Purchase',
    'version': '18.0.0.3',
    'category': 'Sales',
    'summary': 'Sale Advance payment purchase advance payment advance sale payment advance purchase payment sale down payment purchase down payment advance down payment for sales advance down payment for purchase sale purchase advance payment for sale purchase advance',
    'description': """

        Sale Order and Purchase Order Advance Payment in odoo,
        Sale Order Advance Payment in odoo,
        Purchase Order Advance Payment in odoo,
        Make an Advance Payment from Sale and Purchase Order in odoo,
        Advance Payment in odoo,
        Advance Payments will be Listed in Payment Advance Tab in odoo.
        Advance Payment Wizard in odoo,
        Outstanding Credit balance in odoo,
        Outstanding Debit balance in odoo,

    """,
    'author': 'BROWSEINFO',
    "price": 15,
    "currency": 'EUR',
    'website': "https://www.browseinfo.com/demo-request?app=bi_sale_purchase_advance_payment&version=18&edition=Community",
    'depends': ['sale_management','purchase','account','stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/rule.xml',
        'wizard/sale_advance_payment_views.xml',
        'wizard/purchase_advance_payment_views.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/account_payment_views.xml',
        'views/res_config_settings_view.xml',
    
    ],
    'demo': [],
    'test': [],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://www.browseinfo.com/demo-request?app=bi_sale_purchase_advance_payment&version=18&edition=Community',
    "images": ['static/description/Banner.gif'],
}
