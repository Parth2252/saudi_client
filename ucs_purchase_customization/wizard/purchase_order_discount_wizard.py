from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_repr
from collections import defaultdict


class PurchaseOrderDiscount(models.TransientModel):
    _name = 'purchase.order.discount'
    _description = "Purchase Order Discount Wizard"

    purchase_order_id = fields.Many2one(
        'purchase.order', default=lambda self: self.env.context.get('active_id'), required=True)
    company_id = fields.Many2one(related='purchase_order_id.company_id')
    currency_id = fields.Many2one(related='purchase_order_id.currency_id')
    discount_amount = fields.Monetary(string="Amount")
    discount_percentage = fields.Float(string="Percentage")
    discount_type = fields.Selection(
        selection=[
            ('pol_discount', "On All Order Lines"),
            ('po_discount', "Global Discount"),
            ('amount', "Fixed Amount"),
        ],
        default='pol_discount',
    )
    
    @api.constrains('discount_type', 'discount_percentage')
    def _check_discount_amount(self):
        for wizard in self:
            if (
                wizard.discount_type in ('pol_discount', 'po_discount')
                and wizard.discount_percentage > 1.0
            ):
                raise ValidationError(_("Invalid discount amount"))


    def _prepare_discount_line_values(self, product, amount, taxes, description=None):
        self.ensure_one()

        vals = {
            'order_id': self.purchase_order_id.id,
            'product_id': product.id,
            'sequence': 999,
            'price_unit': -amount,
            'taxes_id': [Command.set(taxes.ids)],
        }
        if description:
            # If not given, name will fallback on the standard SOL logic (cf. _compute_name)
            vals['name'] = description

        return vals
    

    def _create_discount_lines(self):
        """Create POline(s) according to wizard configuration"""
        self.ensure_one()
        discount_product = self._get_discount_product()

        if self.discount_type == 'amount':
            vals_list = [
                self._prepare_discount_line_values(
                    product=discount_product,
                    amount=self.discount_amount,
                    taxes=self.env['account.tax'],
                )
            ]
        else: # po_discount
            total_price_per_tax_groups = defaultdict(float)
            for line in self.purchase_order_id.order_line:
                if not line.product_uom_qty or not line.price_unit:
                    continue
                discounted_price = line.price_unit * (1 - (line.discount or 0.0)/100)
                total_price_per_tax_groups[line.taxes_id] += (discounted_price * line.product_uom_qty)

            discount_dp = self.env['decimal.precision'].precision_get('Discount')
            # context = {'lang': self.purchase_order_id._get_lang()} 
            context = {'lang': self.purchase_order_id.partner_id.lang or self.env.user.lang}
            
            if not total_price_per_tax_groups:
                # No valid lines on which the discount can be applied
                return
            elif len(total_price_per_tax_groups) == 1:
                # No taxes, or all lines have the exact same taxes
                taxes = next(iter(total_price_per_tax_groups.keys()))
                subtotal = total_price_per_tax_groups[taxes]
                vals_list = [{
                    **self._prepare_discount_line_values(
                        product=discount_product,
                        amount=subtotal * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Discount: %(percent)s%%",
                            percent=float_repr(self.discount_percentage * 100, discount_dp),
                        ),
                    ),
                }]
            else:
                vals_list = []
                for taxes, subtotal in total_price_per_tax_groups.items():
                    discount_line_value = self._prepare_discount_line_values(
                        product=discount_product,
                        amount=subtotal * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Discount: %(percent)s%%"
                            "- On products with the following taxes %(taxes)s",
                            percent=float_repr(self.discount_percentage * 100, discount_dp),
                            taxes=", ".join(taxes.mapped('name')),
                        ),
                    )
                    vals_list.append(discount_line_value)
        return self.env['purchase.order.line'].sudo().create(vals_list)
    
    
    def _get_discount_product(self):
        """Return product.product used for discount line"""
        self.ensure_one()
        discount_product = self.company_id.sale_discount_product_id
        if not discount_product:
            if (
                self.env['product.product'].check_access_rights('create', raise_exception=False)
                and self.company_id.check_access_rights('write', raise_exception=False)
                and self.company_id._filter_access_rules_python('write')
                and self.company_id.check_field_access_rights('write', ['sale_discount_product_id'])
            ):
                self.company_id.sale_discount_product_id = self.env['product.product'].create(
                    self._prepare_discount_product_values()
                )
            else:
                raise ValidationError(_(
                    "There does not seem to be any discount product configured for this company yet."
                    " You can either use a per-line discount, or ask an administrator to grant the"
                    " discount the first time."
                ))
            discount_product = self.company_id.sale_discount_product_id
        return discount_product
    


    def action_apply_discount(self):
        self.ensure_one()
        self = self.with_company(self.company_id)
        if self.discount_type == 'pol_discount':
            self.purchase_order_id.order_line.sudo().write({'discount': self.discount_percentage*100})
        else:
            self._create_discount_lines()