# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

{
    'name': "Product Vendor Code",
    'category': 'Purchase',
    'version': '18.0.1.0',
    'sequence': 1,
    'summary': """Vendor Product Code, Vendor Product Name, Product Code, Product Name, Vendor Product Code Update, Vendor Product Add Code, Vendor Product Code Add/Update, Purchase Order, Purchase Order Line, Reporting, L4l, Leap, 4, Logic, Leap4logic""",
    'description': """This module helps users to manage specific product code and product name for products.Display the vendor product code and name in the purchase order line and also add/update the product code and name from the purchase order, with this information also shown in reports.""",
    'author': 'Leap4Logic Solutions Private Limited',
    'website': 'https://leap4logic.com/',
    'depends': ['purchase', 'stock', 'mail'],
    'data': [
        'security/security.xml',
        'report/bill_report.xml',
        'report/request_for_quotation_report.xml',
        'views/views_account_move.xml',
        'views/views_product_template.xml',
        'views/views_purchase_order_line.xml',
        'views/views_res_config_settings.xml',
    ],
    'application': True,
    'installation': True,
    'license': 'OPL-1',
    'images': ['static/description/banner.gif'],
    'price': '7.01',
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/GsjKYQ4AiZU',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
