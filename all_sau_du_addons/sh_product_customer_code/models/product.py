# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
import logging
from odoo import api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ShProductTemplate(models.Model):
    _inherit = "product.template"

    sh_product_customer_ids = fields.One2many(
        "sh.product.customer.info", "product_tmpl_id", string="Customer Code"
    )

    code_id = fields.Char(
        related="sh_product_customer_ids.product_code", string="Code", readonly=False
    )

    product_code_name = fields.Char(
        related="sh_product_customer_ids.product_name",
        string="Customer Product Name",
        readonly=False,
    )

    @api.model
    def create(self, vals):
        res = super(ShProductTemplate, self).create(vals)

        if res:
            product_variant = (
                self.env["product.product"]
                .sudo()
                .search([("product_tmpl_id", "=", res.id)])
            )

            if (
                    customer_code := self.env["sh.product.customer.info"]
                            .sudo()
                            .search([("product_tmpl_id", "=", res.id)], order="id desc")
            ):
                for code in customer_code:
                    code.write(
                        {"product_id": product_variant or product_variant[0] or False}
                    )
        return res

    @api.model
    def _search_display_name(self, operator, value):
        return super()._search_display_name(operator, value)


class ShProductProduct(models.Model):
    _inherit = "product.product"

    sh_product_customer_ids = fields.One2many(
        "sh.product.customer.info", "product_id", string="Customer Code"
    )

    code_id = fields.Char(
        related="sh_product_customer_ids.product_code", string="Code", readonly=False
    )

    product_code_name = fields.Char(
        related="sh_product_customer_ids.product_name",
        string="Customer Product Name",
        readonly=False,
    )

    @api.model
    def _search_display_name(self, operator, value):
        partner_id = self.env.context.get("partner_id")
        barcode_values = [value] if operator != "in" else value
        domain = [
            "|",
            "|",
            "|",
            ("name", "ilike", value),
            ("default_code", "ilike", value),
            ("barcode", "in", barcode_values),
            (
                "sh_product_customer_ids",
                "any",
                [
                    "&",
                    ("name.id", "=", partner_id),
                    "|",
                    ("product_code", "ilike", value),
                    ("product_name", "ilike", value),
                ],
            ),
        ]
        return domain

    @api.model
    @api.readonly
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        partner_id = self.env.context.get("partner_id")
        barcode_values = [name] if operator != "in" else name
        domain = [
            "|",
            "|",
            "|",
            ("name", "ilike", name),
            ("default_code", "ilike", name),
            ("barcode", "in", barcode_values),
            (
                "sh_product_customer_ids",
                "any",
                [
                    "&",
                    ("name.id", "=", partner_id),
                    "|",
                    ("product_code", "ilike", name),
                    ("product_name", "ilike", name),
                ],
            ),
        ]

        domain = expression.AND([domain, args or []])
        records = self.search_fetch(domain, ['display_name'], limit=limit)
        return [(record.id, record.display_name) for record in records.sudo()]