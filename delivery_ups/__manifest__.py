{
    'name': "UPS REST Shipping Integration (Custom)",
    'summary': "Send your shipments through UPS and track them online using the official UPS REST APIs. Clean-room community implementation.",
    'category': 'Inventory/Delivery',
    'version': '18.0.1.0.0',
    'application': True,
    'depends': ['stock_delivery', 'mail'],
    'data': [
        'data/ups_package_data.xml',
        'views/delivery_ups_views.xml',
        'views/sale_views.xml',
        'views/res_partner_views.xml',
    ],
    'license': 'LGPL-3',
}
