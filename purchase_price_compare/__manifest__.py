################################################################################
#
#    Odoo Sphere Solutions.
#
#    Copyright (C) 2023-TODAY Odoo Sphere Solutions.
#
#    You can modify it under the terms of the Odoo Proprietary License v1.0,
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    Odoo Proprietary License v1.0 for more details.
#
#    You should have received a copy of the Odoo Proprietary License v1.0 along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#####################################################################################
{
    'name': "Purchase Price Comparison | Comparison of purchase price with Pivot View",
    'version': '18.0.1.0.0',
    'summary': """1. The module integrates with a pivot view, providing users with a dynamic and interactive way to analyze and compare purchase quotations. Pivot views often allow users to arrange and summarize data flexibly.""",
    'description': """1. The module integrates with a pivot view, providing users with a dynamic and interactive way to analyze and compare purchase quotations. Pivot views often allow users to arrange and summarize data flexibly.""",
    'author': "Odoo Sphere Solutions",
    'company': 'Odoo Sphere Solutions',
    'maintainer': 'Odoo Sphere Solutions',
    'category': 'Purchase',
    'depends': ['purchase'],
    'data': ['views/purchase_report_pivot_views.xml'],
    'assets': {},
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 10.7,
    'installable': True,
    'auto_install': False,
    'application': False,
}
