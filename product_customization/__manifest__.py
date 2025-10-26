# -*- coding: utf-8 -*-
{
    'name': "Product Customization",
    'summary': "Product Customization",
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'depends': ['base','product','sale','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_view.xml',
        'views/product_template_view.xml',
        'views/product_product_view.xml',
    ]
}

