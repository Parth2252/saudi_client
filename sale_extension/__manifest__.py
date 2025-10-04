# -*- coding: utf-8 -*-
{
    'name': "Sale Extended new",
    'version': '18.0',
    'summary': 'Sale New',
    'sequence': 10,
    'description': """
Sale Extended
    """,
    'category': 'Custom',
    'website': 'self.com',
    'depends': ['base','stock','sale', 'mail', 'sale_pdf_quote_builder', 'sh_product_customer_code','web','product','l10n_sa','l10n_gcc_invoice','account', 'hr','uom','sale_stock'],
    'data': [
        # 'security/ir.model.access.csv',
        "security/security.xml",

        'report/commercial_report.xml',
        'report/technical_offer.xml',
        'report/sales_invoice_report.xml',
        # 'report/report_invoice.xml',
        # 'views/templates.xml',
        'views/packaging_list_template.xml',
        'views/sale_order_line.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        'views/res_partner.xml',

    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'sale_extension/static/src/css/offered_placeholder.css',
        ],
    },

    'installable': True,
    'application': True,

    'license': 'OPL-1',
}
