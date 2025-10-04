# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Internal Payment Transfer ',
    "author": "TechUltra Solutions Private Limited",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolution.com",
    'category': 'account',
    'version': '18.0.0.0.0',
    'summary': """Internal Payment Transfer in Odoo is used to move funds between different internal bank or cash accounts within the same company. It helps manage liquidity across multiple accounts and ensures proper accounting entries are made without involving external vendors or customers.
    Internal Payment Transfer
        tus
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        Internal Transfer
        Internal Payment Transfer
        Internal Payment Transfer odoo18
        Inter-account transfer
        journal transfer
        Fund movement
        Same-bank transfer
        fund transfer
        Intra-company transfer
        Account-to-account
        Payment routing
        Ledger adjustment
        Journal entry: internal payment
        Accounting move
        Reconcile internal payment
        Inter-entity payment
        Odoo internal transfer
        Internal cash book
        Intercompany journal
        Internal bank account
        Transfer voucher
        Offset entry
        cash transfer
        Internal transfer
        """
    ,
    'description': """ In Odoo, an Internal Payment Transfer is a type of payment transaction where the company transfers money from one of its own bank or cash accounts to another.
       Internal Payment Transfer
        tus
        TUS
        TechUltra Solutions Private Limited
        techUltra solutions private limited
        Internal Transfer
        Internal Payment Transfer
        Internal Payment Transfer odoo18
        Inter-account transfer
        journal transfer
        Fund movement
        Same-bank transfer
        fund transfer
        Intra-company transfer
        Account-to-account
        Payment routing
        Ledger adjustment
        Journal entry: internal payment
        Accounting move
        Reconcile internal payment
        Inter-entity payment
        Odoo internal transfer
        Internal cash book
        Intercompany journal
        Internal bank account
        Transfer voucher
        Offset entry
        cash transfer
        Internal transfer
    """,
    'depends': ['account'],
    'data': [

        'views/account_payment_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [

        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 11.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    "license": "OPL-1",
}
