# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Email CC BCC & Reply To option Odoo',
    'version': '18.0.0.2',
    'category': 'Extra Tools',
    'summary': 'Email CC Email CC Email CC and BCC default Reply to on email default CC on email Default BCC on email bcc email cc mail bcc mail email cc with reply to email option advance email option compose email with cc compose bcc email compose mail cc compose bcc',
    'description' :"""
      
        Email CC BCC With Reply to Option in Odoo,
        Email CC in odoo,
        Email BCC in odoo,
        Email Reply to option in odoo,
        Default CC & BCC for Email in odoo,
        Default Reply to for Email in odoo,
        Send Mail to the Customers with CC & BCC in odoo,
        Send Mail to the Customers with Reply to in odoo,

    """,
    'author': 'BROWSEINFO',
    "price": 20,
    "currency": 'EUR',
    'website': "https://www.browseinfo.com/demo-request?app=bi_email_cc&version=18&edition=Community",
    'depends': ['sale_management','account'],
    'data': [
        'views/res_settings_views.xml',
        'views/sale_mail_views.xml',
        'views/account_mail_views.xml',
        'views/mail_views.xml',
    
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'live_test_url':'https://www.browseinfo.com/demo-request?app=bi_email_cc&version=18&edition=Community',
    "images":['static/description/Banner.gif'],
}
