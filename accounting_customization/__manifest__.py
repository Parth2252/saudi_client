# See LICENSE file for full copyright and licensing details.
{
    "name": "Accounting Customization",
    "version": "18.0.1.0.0",
    "category": "account",
    "depends": ["base", "sale", "account"],
    "data": [
        "data/account_data.xml",
        "wizard/account_payment_register_views.xml",
        "views/account_payment_views.xml",
        "views/account_move_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "accounting_customization/static/src/views/account_dashboard.js",
            "accounting_customization/static/src/views/account_dashboard.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3"
}
