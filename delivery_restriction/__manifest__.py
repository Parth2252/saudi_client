# See LICENSE file for full copyright and licensing details.
{
    "name": "Delivery Restriction",
    "version": "18.0.1.0.0",
    "category": "stock/delivery",
    "depends": ["base", "sale", "stock", "sale_stock", "account", "sale_management"],
    "data": [
        "views/stock_picking_views.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml"
    ],
    "installable": True,
    "auto_install": False,
}
