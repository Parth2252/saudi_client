from odoo import models, fields, api, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date
from datetime import timedelta


class ProductProduct(models.Model):
    _inherit = "product.product"

    attachment_ids = fields.One2many(
        "ir.attachment",
        "res_id",
        string="Attachments",
        domain="[('res_model', '=', 'product.product')]",
        readonly=True,
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pr_number = fields.Char(string="PR Number")
    sr_no_so = fields.Integer(string="Order No")
    sh_line_customer_code = fields.Char(
        string="Customer Product Code",
        compute="_compute_sh_line_customer_code",
        readonly=False,
        store=True,
    )
    sh_line_customer_product_name = fields.Char(string="Customer Product Name")
    # offered_description_id = fields.Many2one(
    #     'product.product', string="Offered Description", readonly=False)

    offered_description_id = fields.Many2one(
        "product.product",
        string="Offered Description",
        domain=[("sale_ok", "=", True)],
        required=False,
    )

    # offered_image = fields.Binary(related='product_id.image_1920', readonly=True, store=True)

    offered_image = fields.Binary(
        string="Image for Report", compute="_compute_offered_image", store=True
    )

    delivery_time = fields.Integer(string="Delivery Time")
    ts_code = fields.Char(string="TS Code", store=True, readonly=False)
    blank = fields.Monetary(
        string="Blank",
        currency_field="currency_id",
        compute="_compute_blank",
        store=False,
    )

    translated_product_name = fields.Char()

    delivery_time_display = fields.Char(
        string="Delivery Time", compute="_compute_delivery_time_display"
    )

    # product_category_id = fields.Many2one(
    #     related="product_template_id.categ_id",
    #     string="Product Category",
    #     store=True,
    #     readonly=False,
    # )

    # offered_product_category_id = fields.Many2one(
    #     related="offered_description_id.categ_id",
    #     string="Offered Product Category",
    #     store=True,
    #     readonly=False,
    # )

    # customization start.
    is_not_available = fields.Boolean(copy=False)

    delivery_date = fields.Datetime(
        copy=False, compute="_compute_delivery_date", store=True, readonly=False
    )

    product_url = fields.Char(string="Product URL")

    product_vendor_id = fields.Many2one(
        "res.partner", string="Vendor", domain="[('id', 'in', allowed_vendor_ids)]"
    )

    allowed_vendor_ids = fields.Many2many(
        "res.partner", compute="_compute_allowed_vendors", store=False
    )

    vendor_price = fields.Float(string="Vendor Price")

    is_vendor_price = fields.Boolean(compute="_compute_is_vendor_price")

    vendor_currency_id = fields.Many2one("res.currency", copy=False, string="Vendor Currency")

    def _compute_is_vendor_price(self):
        for rec in self:
            rec.is_vendor_price = bool(rec.vendor_price)

    @api.depends("product_id", "offered_description_id")
    def _compute_allowed_vendors(self):
        for line in self:
            vendors = self.env["res.partner"]

            # Product-based vendors
            product = line.offered_description_id or line.product_id
            if product:
                product_vendors = product.seller_ids.mapped("partner_id")
                vendors |= product_vendors

            # All contacts with is_vendor = True
            vendor_contacts = self.env["res.partner"].search([("is_vendor", "=", True)])
            vendors |= vendor_contacts

            line.allowed_vendor_ids = vendors

            # Auto set first seller if no vendor manually selected
            if product:
                seller = product.seller_ids[:1]
                line.vendor_currency_id = seller.currency_id.id
                if seller and not line.product_vendor_id and not line.vendor_price:
                    line.product_vendor_id = seller.partner_id.id
                    line.vendor_price = seller.price
                    line.product_url = seller.product_url

    # customization end.

    @api.onchange("is_not_available")
    def _onchange_is_not_available(self):
        """Update price based on availability"""
        for line in self:
            if line.is_not_available:
                line.price_unit = 0.0
                line.product_uom_qty = 0.0
            else:
                if line.product_id:
                    line.price_unit = line.product_id.list_price

    @api.depends("order_id.date_order", "delivery_time")
    def _compute_delivery_date(self):
        for line in self:
            if line.order_id.date_order and line.delivery_time:
                line.delivery_date = line.order_id.date_order.date() + timedelta(
                    days=line.delivery_time
                )
            else:
                line.delivery_date = line.delivery_date or False

    # @api.onchange(
    #     "product_id",
    #     "offered_description_id",
    #     "product_category_id",
    #     "offered_product_category_id",
    # )
    # def _onchange_product_category_update_ts_code(self):
    #     for line in self:
    #         print("\n\n\n ---- line.offered_description_id ---", line.offered_description_id)
    #         print("\n\n\n ----- line.product_id ----", line.product_id, line.product_id.default_code)
    #         product = line.offered_description_id or line.product_template_id
    #         print("\n\n\n ---- product ---", product, product.default_code)
    #         if product:
    #             line.ts_code = product.default_code

    @api.depends("product_id", "offered_description_id", "order_id.partner_id")
    def _compute_sh_line_customer_code(self):
        for line in self:
            customer = line.order_id.partner_id
            # Priority: use offered_description_id if available
            product = line.offered_description_id or line.product_id
            customer_info = False
            line.ts_code = product.default_code
            if customer and product:
                customer_info = (
                    self.env["sh.product.customer.info"]
                    .sudo()
                    .search(
                        [
                            ("name", "=", customer.id),
                            "|",
                            ("product_id", "=", product.id),
                            ("product_tmpl_id", "=", product.product_tmpl_id.id),
                        ],
                        limit=1,
                    )
                )
            if customer_info:
                line.sh_line_customer_code = customer_info.product_code or False
                line.sh_line_customer_product_name = customer_info.product_name or False
            else:
                line.sh_line_customer_code = product.default_code or False
                line.sh_line_customer_product_name = product.name or False

            if not line.offered_description_id:
                line.price_unit = line.product_id.list_price

    @api.depends("delivery_time")
    def _compute_delivery_time_display(self):
        for rec in self:
            if rec.delivery_time is not None and not rec.is_not_available:
                days = rec.delivery_time

                if days == 0:
                    rec.delivery_time_display = "Ex-Stock"
                elif days < 1:
                    rec.delivery_time_display = "Yesterday"
                elif days == 1:
                    rec.delivery_time_display = "Tomorrow"
                elif days % 7 == 0:
                    weeks = days // 7
                    rec.delivery_time_display = (
                        f"{weeks} WEEK{'S' if weeks > 1 else ''}"
                    )
                else:
                    rec.delivery_time_display = f"{days} DAY{'S' if days > 1 else ''}"
            else:
                rec.delivery_time_display = ""

    # @api.depends('offered_description_id')
    # def _compute_offered_description_display(self):
    #     for line in self:
    #         line.offered_description_display = line.offered_description_id.display_name if line.offered_description_id else "AS SPECIFIED"

    @api.depends(
        "offered_description_id", "product_id", "product_uom", "product_uom_qty"
    )
    def _compute_price_unit(self):
        for line in self:
            # Don't compute the price for deleted lines.
            if not line.order_id:
                continue
            # check if the price has been manually set or there is already invoiced amount.
            # if so, the price shouldn't change as it might have been manually edited.
            if line.offered_description_id:
                line = line.with_company(line.company_id)
                line.price_unit = line.offered_description_id.list_price
            else:
                super(SaleOrderLine, self)._compute_price_unit()

    def _compute_blank(self):
        for order in self:
            order.blank = 0.0

    @api.depends("offered_description_id", "product_id")
    def _compute_offered_image(self):
        for line in self:
            if line.offered_description_id and line.offered_description_id.image_1920:
                line.offered_image = line.offered_description_id.image_1920
            else:
                line.offered_image = line.product_id.image_1920

    def sale_order_line_sequence(self):
        """Generate auto sequence for sale order."""
        number = 1
        for record in self.order_id.order_line:
            if not record.display_type:
                record.sr_no_so = number
                number += 1

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-create sequence for purchase order lines."""
        lines = super().create(vals_list)
        for line in lines:
            line.sale_order_line_sequence()
            line._update_supplier_info()
        return lines

    # def write(self, vals):
    #     res = super(SaleOrderLine, self).write(vals)
    #     if (
    #         "product_vendor_id" in vals
    #         or "vendor_price" in vals
    #         or "vendor_currency_id" in vals
    #         or "product_url" in vals
    #     ):
    #         self._update_supplier_info()
    #     return res

    def _update_supplier_info(self):
        """Create product.supplierinfo based on SO line vendor details if not exists"""
        for line in self:
            target_product = line.offered_description_id or line.product_id
            if not target_product and not line.product_vendor_id:
                continue

            # Search if a supplier info already exists for this vendor and product
            domain = [
                ("partner_id", "=", line.product_vendor_id.id),
                ("product_tmpl_id", "=", target_product.product_tmpl_id.id),
            ]
            supplier_info = self.env["product.supplierinfo"].search(domain, limit=1)

            if not supplier_info:
                # Create new record ONLY if it doesn't exist
                vals = {
                    "partner_id": line.product_vendor_id.id,
                    "product_tmpl_id": target_product.product_tmpl_id.id,
                    "min_qty": 1.0,
                }
                if line.vendor_price:
                    vals["price"] = line.vendor_price
                if line.vendor_currency_id:
                    vals["currency_id"] = line.vendor_currency_id.id
                if line.product_url:
                    vals["product_url"] = line.product_url

                self.env["product.supplierinfo"].create(vals)


    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_product_qty(self):
        for line in self:
            if not line.product_id or not line.product_uom or not line.product_uom_qty:
                line.product_qty = 0.0
                continue
            line.product_qty = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id, raise_if_failure=False
            )

    def show_customer_product_name(self):
        """Return True if customer product name should be shown."""
        for line in self:
            if (
                line.sh_line_customer_product_name
                and line.sh_line_customer_product_name.strip()
            ):
                return True
        return False

    def return_item_code(self):
        sh_customer_info_env = self.env["sh.product.customer.info"]
        so_partner_id = self.order_id.partner_id
        product_id = self.product_id

        if so_partner_id and product_id:
            item_code = sh_customer_info_env.search(
                [
                    ("name", "=", so_partner_id.id),
                    ("product_id", "=", product_id.id),
                ],
                limit=1,
            )
            return item_code.product_code or product_id.default_code
        else:
            return product_id.default_code

    def return_ts_code(self):
        # sh_customer_info_env = self.env["sh.product.customer.info"]
        # so_partner_id = self.order_id.partner_id
        # product_id = self.product_id
        # if self.offered_description_id:
        #     product_id = self.offered_description_id

        # if so_partner_id and product_id:
        #     ts_code = sh_customer_info_env.search(
        #         [
        #             ("name", "=", so_partner_id.id),
        #             ("product_id", "=", product_id.id),
        #         ],
        #         limit=1,
        #     )
        #     return ts_code.product_code or product_id.default_code
        # else:
        #     return product_id.default_code

        if self.offered_description_id:
            return self.offered_description_id.default_code
        else:
            return self.product_id.default_code



class UoM(models.Model):
    _inherit = "uom.uom"

    def _compute_quantity(
        self, qty, to_unit, round=True, rounding_method="UP", raise_if_failure=True
    ):
        """Override to remove category validation"""
        if not self or not qty:
            return qty
        self.ensure_one()

        if self == to_unit:
            amount = qty
        else:
            amount = qty / self.factor
            if to_unit:
                amount = amount * to_unit.factor

        if to_unit and round:
            amount = tools.float_round(
                amount,
                precision_rounding=to_unit.rounding,
                rounding_method=rounding_method,
            )

        return amount
