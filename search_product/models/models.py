# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SearchProduct(models.Model):
    _inherit = "product.template"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = list(args or [])
        if not name:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit
            )

        domain = [
            "|",
            "|",
            ("name", operator, name),
            ("sh_product_customer_ids.product_code", operator, name),
            ("sh_product_customer_ids.product_name", operator, name),
        ]
        if args:
            domain = ["&"] + args + domain

        products = self.search_fetch(domain, ["display_name"], limit=limit)
        if not products:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit
            )

        return [(rec.id, rec.display_name) for rec in products]


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = list(args or [])
        if not name:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit
            )

        domain = [
            "|",
            "|",
            ("name", operator, name)(
                "sh_product_customer_ids.product_code", operator, name
            ),
            ("sh_product_customer_ids.product_name", operator, name),
        ]
        if args:
            domain = ["&"] + args + domain

        products = self.search_fetch(domain, ["display_name"], limit=limit)
        if not products:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit
            )

        return [(rec.id, rec.display_name) for rec in products]
