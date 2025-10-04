{
    "name": "Display Creation Date",
    "version": "18.0.1.0.0",
    "depends": ["account", "purchase", "stock"],
    "category": "Accounting/Purchase/Stock",
    "summary": "Display the creation date in customer invoice, vendor bills, purchase order, RFQ and inventory. also displayed the payment date at vendor bill",
    "data": [
        "data/account_data.xml",
        "views/account_move_view.xml",
        "views/purchase_order_view.xml",
        "views/stock_picking_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
