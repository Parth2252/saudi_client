{
    'name': 'Product Offer Relation',
    'version': '18.0.1.0.0',
    'summary': 'Adds Offer and Main Product tabs to Product Template',
    'category': 'Product',
    'depends': ['product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
