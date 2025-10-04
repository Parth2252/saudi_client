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
from odoo import models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.report'

    @api.model
    def compare_purchase_price(self):
        domain = []
        if self.env.context.get('active_ids'):
            domain = [('order_id', 'in', self.env.context.get('active_ids', []))]
        return {
            'name': _('Price Comparison'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.report',
            'view_mode': 'pivot',
            'domain': domain,
            'context': {
                'group_expand': True,
            }
        }
