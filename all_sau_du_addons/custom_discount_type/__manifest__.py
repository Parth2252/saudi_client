{
    'name': 'Custom Discount Type',
    'version': '18.0.1.0.0',
    'category': 'Sales/Purchase/Accounting',
    'summary': 'Add discount type (fixed/percentage) in SO, PO, and Invoice lines',
    'depends': ['sale_management', 'purchase', 'account'],
    'data': [
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
}
