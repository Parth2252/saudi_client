{
    'name': 'Stock Inventory Import Location Wise',
    'version': '18.0',
    'summary': 'Import product stock/inventory from Excel/CSV location wise',
    'category': 'Inventory',
    'author': 'Antigravity',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_inventory_wizard_view.xml',
        'wizard/stock_inventory_log_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
