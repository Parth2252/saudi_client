import base64
from io import BytesIO
from odoo import models, fields, api
import qrcode


class StockPickingProductDetail(models.Model):
    _name = 'stock.picking.product.detail'
    _description = 'Stock Picking Product Detail'

    picking_id = fields.Many2one('stock.picking', string="Picking Reference", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", domain="[('id', 'in', available_product_ids)]")
    available_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_available_product_ids',
        store=False
    )
    part_no = fields.Char(string="Part No")
    manuanl_qty = fields.Integer(string="Quantity")
    manuanl_remark = fields.Char(string="Remark")
    offered_description_id = fields.Many2one(
        'product.product',
        string="Offered Description",
        domain=[('sale_ok', '=', True)],
        required=False
    )
    ts_code = fields.Char(
        string="TS Code",  # Internal Reference
        store=False,
        readonly=False
    )

    item_code = fields.Char(
        string="Item Code",  # Customer Product Code
        store=False
    )

    @api.depends('picking_id')
    def _compute_available_product_ids(self):
        for rec in self:
            if rec.picking_id:
                product_ids = rec.picking_id.move_ids_without_package.mapped('product_id').ids
                rec.available_product_ids = [(6, 0, product_ids)]
            else:
                rec.available_product_ids = [(6, 0, [])]




class StockPicking(models.Model):
    _inherit = "stock.picking"

    product_detail_ids = fields.One2many(
        'stock.picking.product.detail',
        'picking_id',
        string="Product Details"
    )
    acknowledgement = fields.Text(
        string='Acknowledgement',
        default='We acknowledge receipt of above goods complete and inspection by us showed that goods are free from any defects or damage.'
    )

    qr_code = fields.Binary("QR Code", attachment=True, readonly=True)
    qr_code_url = fields.Char("QR Code URL", compute="_compute_qr_code_url", store=False)
    sale_user_id = fields.Many2one(
        related='sale_id.user_id',
        string='Salesperson',
        store=True,
        readonly=False, default = lambda self: self.env.user
    )
    user_id = fields.Many2one(default=lambda self: self.env.user, string='Salesperson', store=True, readonly=False)
    approver_user_id = fields.Many2one('res.users', default=lambda self: self.env.uid, string='Issued By', store=True,
                                       readonly=True)
    validated_datetime = fields.Datetime(string="Validated On")
    validated_by_id = fields.Many2one('res.users', string='Validated By', readonly=True)
    validated_employee_id = fields.Many2one(
        'hr.employee', string='Validated Employee',
        compute='_compute_validated_employee', store=True)
    contact_id = fields.Many2one('res.partner', 'Customer Contact', readonly=True)

    partner_invoice_id = fields.Many2one(
        'res.partner',
        string='Invoice Address',
        readonly=False,
        store=True
    )
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Shipping Address',
        readonly=False,
        store=True
    )
    client_order_ref = fields.Char(string="PO Reference", related='sale_id.client_order_ref', readonly=False)
    porder_ref = fields.Char(string="PO Reference", readonly=False)

    purchase_order_names = fields.Char(
        string='PO Number(s)', compute='_compute_purchase_order_names', store=False
    )

    @api.depends('move_ids_without_package.purchase_line_id.order_id')
    def _compute_purchase_order_names(self):
        for picking in self:
            po_names = picking.move_ids_without_package \
                .mapped('purchase_line_id.order_id.name')
            # Remove duplicates and join
            picking.purchase_order_names = ', '.join(sorted(set(po_names)))

    @api.onchange('partner_id')
    def _onchange_partner_id_address(self):
        """ Auto-populate invoice and shipping addresses based on partner_id. """
        for rec in self:
            if rec.partner_id:
                addresses = rec.partner_id.address_get(['invoice', 'delivery'])
                rec.partner_invoice_id = addresses.get('invoice')
                rec.partner_shipping_id = addresses.get('delivery')


    @api.depends('validated_by_id')
    def _compute_validated_employee(self):
        for rec in self:
            employee = self.env['hr.employee'].search([('user_id', '=', rec.validated_by_id.id)], limit=1)
            rec.validated_employee_id = employee


    def button_validate(self):
        res = super().button_validate()

        for picking in self:
            if picking.state == 'done':
                picking.approver_user_id = self.env.user
                picking.validated_by_id = self.env.user
                picking.validated_datetime = fields.Datetime.now()

        return res


    def _compute_qr_code_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for picking in self:
            picking.qr_code_url = f"{base_url}/web#id={picking.id}&model=stock.picking&view_type=form"

    def generate_qr_code(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for picking in self:
            if not picking.id:
                picking.qr_code = False
                continue

            qr_url = f"{base_url}/web#id={picking.id}&model=stock.picking&view_type=form"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_image = base64.b64encode(buffer.getvalue())
            picking.qr_code = qr_image

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.generate_qr_code()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'name' in vals or 'state' in vals:
            self.generate_qr_code()
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    # description = fields.Text(
    #     string="SO Description",
    #     related='sale_line_id.name',
    #     store=False
    # )

    remark = fields.Char(string="Remarks")


    # ts_code = fields.Char(
    #     string="TS Code",
    #     related='sale_line_id.product_id.default_code',
    #     store=False
    # )


    # item_code = fields.Char(
    #     string="Item Code",
    #     related='sale_line_id.product_id.default_code',
    #     store=False
    # )


    # sh_line_customer_code = fields.Char(
    #     string="Customer Product Code",
    #     related='sale_line_id.sh_line_customer_code',
    #     store=False
    # )

    sh_line_customer_code = fields.Char(
        string="Customer Product Code",
        compute="_compute_sh_line_customer_code",
        store=False
    )

    ts_code = fields.Char(
        string="TS Code",  # Internal Reference
        compute="_compute_ts_code",
        store=False,
        readonly=False
    )

    item_code = fields.Char(
        string="Item Code",  # Customer Product Code
        compute="_compute_item_code",
        store=False
    )

    description = fields.Text(
        string="SO Description",  # Customer Product Name
        compute='_compute_description',
        store=False,
        readonly=False
    )

    @api.depends('product_id')
    def _compute_ts_code(self):
        for move in self:
            move.ts_code = move.product_id.default_code or ''

    @api.depends('picking_id.partner_id', 'product_id', 'sale_line_id')
    def _compute_item_code(self):
        for move in self:
            if move.sale_line_id and move.sale_line_id.sh_line_customer_code:
                move.item_code = move.sale_line_id.sh_line_customer_code
            elif move.product_id and move.picking_id.partner_id:
                customer_info = self.env['sh.product.customer.info'].search([
                    ('name', '=', move.picking_id.partner_id.id),
                    ('product_id', '=', move.product_id.id)
                ], limit=1)
                move.item_code = customer_info.product_code or ''
            else:
                move.item_code = ''

    @api.depends('picking_id.partner_id', 'product_id', 'sale_line_id')
    def _compute_description(self):
        for move in self:
            if move.sale_line_id and move.sale_line_id.sh_line_customer_product_name:
                move.description = move.sale_line_id.sh_line_customer_product_name
            elif move.product_id and move.picking_id.partner_id:
                customer_info = self.env['sh.product.customer.info'].search([
                    ('name', '=', move.picking_id.partner_id.id),
                    ('product_id', '=', move.product_id.id)
                ], limit=1)
                move.description = customer_info.product_name or move.product_id.name or ''
            elif move.product_id:
                move.description = move.product_id.name
            else:
                move.description = ''

    @api.depends('sale_line_id', 'product_id', 'picking_id.partner_id')
    def _compute_sh_line_customer_code(self):
        for move in self:
            if move.sale_line_id:
                move.sh_line_customer_code = move.sale_line_id.sh_line_customer_code
            elif move.product_id and move.picking_id.partner_id:
                customer_info = self.env['sh.product.customer.info'].search([
                    ('name', '=', move.picking_id.partner_id.id),
                    ('product_id', '=', move.product_id.id)
                ], limit=1)
                move.sh_line_customer_code = customer_info.product_code or ''
            else:
                move.sh_line_customer_code = ''
