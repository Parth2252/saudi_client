# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
	'name': "Purchase Product Price Comparison",
	'version': "18.0.0.0",
	'category': "Purchases",
	'summary': "Purchase Order Price Comparison on Request for Quotation Compare Product Price for PO Vendor Price Comparison Purchase Orders Compare by Vendor Comparison of Purchase Price Purchase Price Comparison RFQ Price Comparison Quotation Price Comparison",
	'description': """
	
		Purchase Product Price Comparison Odoo App helps users to compare price of purchase order in pivot view. User can print or download purchase price comparison in excel format.	

	""",
	'author': 'BROWSEINFO',
    "price": 20,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.com/demo-request?app=bi_product_cost_price_comparison&version=18&edition=Community',
    'depends': ['base', 'purchase'],
	'data': [
			'views/view_price_comparison.xml',
			],
	'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://www.browseinfo.com/demo-request?app=bi_product_cost_price_comparison&version=18&edition=Community',
    "images":['static/description/Banner.gif'],
}

