from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_repr
from collections import defaultdict


class AccountMoveDiscount(models.TransientModel):
    _name = 'account.move.discount'
    _description = "Account Move Discount Wizard"

    account_move_id = fields.Many2one(
        'account.move', default=lambda self: self.env.context.get('active_id'), required=True)
    company_id = fields.Many2one(related='account_move_id.company_id')
    currency_id = fields.Many2one(related='account_move_id.currency_id')
    discount_amount = fields.Monetary(string="Amount")
    discount_percentage = fields.Float(string="Percentage")
    discount_type = fields.Selection(
        selection=[
            ('aml_discount', "On All Move Lines"),
            ('ml_discount', "Global Discount"),
            ('amount', "Fixed Amount"),
        ],
        default='aml_discount',
    )
    
    @api.constrains('discount_type', 'discount_percentage')
    def _check_discount_amount(self):
        for wizard in self:
            if (
                wizard.discount_type in ('aml_discount', 'ml_discount')
                and wizard.discount_percentage > 1.0
            ):
                raise ValidationError(_("Invalid discount amount"))


    def _prepare_discount_line_values(self, product, amount, taxes, description=None):
        self.ensure_one()

        vals = {
            'move_id': self.account_move_id.id,
            'product_id': product.id,
            'sequence': 999,
            'price_unit': -amount,
            'tax_ids': [Command.set(taxes.ids)],
        }
        if description:
            # If not given, name will fallback on the standard SOL logic (cf. _compute_name)
            vals['name'] = description

        return vals
    

    def _create_discount_lines(self):
        """Create POline(s) according to wizard configuration"""
        self.ensure_one()
        discount_product = self._get_discount_product()
        print("Discount Product -> ",discount_product)
        

        if self.discount_type == 'amount':
            vals_list = [
                self._prepare_discount_line_values(
                    product=discount_product,
                    amount=self.discount_amount,
                    taxes=self.env['account.tax'],
                )
            ]
            
            
            
        else: # ml_discount
            total_price_per_tax_groups = defaultdict(float)
            for line in self.account_move_id.invoice_line_ids:
                if not line.quantity or not line.price_unit:
                    continue
                discounted_price = line.price_unit * (1 - (line.discount or 0.0)/100)
                total_price_per_tax_groups[line.tax_ids] += (discounted_price * line.quantity)

            discount_dp = self.env['decimal.precision'].precision_get('Discount')
            # context = {'lang': self.account_move_id._get_lang()} 
            context = {'lang': self.account_move_id.partner_id.lang or self.env.user.lang}
            
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
        res = self.env['account.move.line'].sudo().create(vals_list)
              
        return res
    
    def _prepare_discount_product_values(self):
        self.ensure_one()
        return {
            'name': _('Discount'),
            'type': 'service',
            'invoice_policy': 'order',
            'list_price': 0.0,
            'company_id': self.company_id.id,
            'taxes_id': None,
        }
        
        
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
        if self.discount_type == 'aml_discount':
            self.account_move_id.invoice_line_ids.sudo().write({'discount': self.discount_percentage*100})
        else:
            pass
            self._create_discount_lines()