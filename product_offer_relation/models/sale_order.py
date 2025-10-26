from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            for line in order.order_line:
                main_product = line.product_id
                offer_product = line.offered_description_id

                if offer_product:
                    main_template = main_product.product_tmpl_id
                    offer_template = offer_product.product_tmpl_id

                    # Add offer product to main product's offer tab
                    existing_offer = self.env['product.offer.line'].search([
                        ('product_tmpl_id', '=', main_template.id),
                        ('product_id', '=', offer_product.id),
                    ], limit=1)

                    if not existing_offer:
                        self.env['product.offer.line'].create({
                            'product_tmpl_id': main_template.id,
                            'product_id': offer_product.id,
                            'sale_order_id': order.id
                        })

                    # 🔹 Add main product to offer product's main tab
                    existing_main = self.env['product.main.line'].search([
                        ('product_tmpl_id', '=', offer_template.id),
                        ('product_id', '=', main_product.id),
                    ], limit=1)

                    if not existing_main:
                        self.env['product.main.line'].create({
                            'product_tmpl_id': offer_template.id,
                            'product_id': main_product.id,
                            'sale_order_id': order.id
                        })

        return res
