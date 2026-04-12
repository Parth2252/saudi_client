{
    "name": "Partner Fuzzy Duplicate Restriction",
    "version": "18.0.1.0.0",
    "summary": "Prevents duplicate contacts based on name (80% similarity match) and unique Customer/Vendor IDs",
    "depends": ["base", "contacts", "bi_custmor_vendor_unquie_code"],
    "data": [
        "views/res_partner_views.xml",
        "data/server_action.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
