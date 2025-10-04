# -*- coding: utf-8 -*-
{
    'name': "POS Arabic Product Name",

    'summary': """
        Show English and Arabic Name on POS Screen at same time""",

    'description': """
        Show English and Arabic Name on POS Screen at same time
    """,

    'author': "Smart Tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'POS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],
    'license': 'OPL-1',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'images': ['static/description/1.png'],
    # only loaded in demonstration mode
    
    'qweb': ['static/src/xml/product_arabic_name.xml'],
}
