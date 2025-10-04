{
    "name": "Vendor Bill Send Receipt",
    "version": "18.0.1.0.0",
    "summary": "Send payment receipt from vendor bill form view",
    "category": "Accounting",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
