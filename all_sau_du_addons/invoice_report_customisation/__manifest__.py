{
    "name": "Invoice Report Customisation",
    "version": "18.0.1.0.0",
    "summary": "Invoice Report Layout Changes",
    "category": "Accounting",
    "depends": ["account", "l10n_gcc_invoice", "web", "l10n_sa"],
    "data": [
        "report/report_invoice.xml",
        "report/external_layout.xml",
        "report/external_layout_bubble.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
