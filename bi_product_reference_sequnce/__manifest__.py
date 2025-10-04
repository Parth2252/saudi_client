# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Product Internal Reference based on Product Category | Auto Generate Product Code | Custom Product Code Generator",
    "version": "18.0.0.1",
    "category": "Warehouse",
    'summary': "auto generate product internal reference based on category auto assign product reference sku generator product reference based on status unique product code product code based on category product internal reference based on category unique product code",
    'description': """Generate Product Internal Reference based on Product Category Odoo App automates the generation of unique product internal references based on product categories. User can set sequence to generate product codes dynamically on product category and based on that internal reference will be generated and assigned to product automatically. This ensures a well-structured and standardized product identification system, making it easier to manage and track inventory efficiently. Additionally, the app allows the assignment of internal references based on the active or inactive status of product categories.""",
    'author': "BROWSEINFO",
    'website': "https://www.browseinfo.com/demo-request?app=bi_product_reference_sequnce&version=18&edition=Community",
    "price": 25.00,
    "currency": 'EUR',
    "depends": ['product','stock'],
    "data": [
        'views/product_category.xml',
        'views/product_template.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "live_test_url": 'https://www.browseinfo.com/demo-request?app=bi_product_reference_sequnce&version=18&edition=Community',
    'license': 'OPL-1',
    "images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
