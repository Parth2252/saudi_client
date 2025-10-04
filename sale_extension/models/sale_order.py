from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    quote_desc = fields.Char(string="RFQ / Description", required=True)

# NEW
    contact_id = fields.Many2one('res.partner', 'Customer Contact', domain=[('type', '=', 'contact')], readonly=True)
# NEW

    # Overrite field to make compute.
    commitment_date = fields.Datetime(
        string="Commitment Date",
        compute="_compute_commitment_date",
        store=True,
        readonly=False,
    )

    # Added new field.
    po_expire_date = fields.Datetime(copy=False)

    validity_duration_days = fields.Integer(
        string="Validity Duration (Days)",
        compute="_compute_validity_duration_days",
        store=True,
    )

    @api.depends('date_order', 'validity_date', 'state')
    def _compute_validity_duration_days(self):
        for order in self:
            if order.state not in ('sale'):  # Only in quotation state
                if order.date_order and order.validity_date:
                    order.validity_duration_days = (order.validity_date - order.date_order.date()).days
                else:
                    order.validity_duration_days = 0
            else:
                # After confirmation don't recalculate
                order.validity_duration_days = order.validity_duration_days or 0

    def action_confirm(self):
        for order in self:
            if not order.client_order_ref:
                raise UserError(_("PO Reference is required before confirming the order."))
            # Raise the validation if delivery date is missing in sol.
            # in sale.order (or purchase.order) wherever you validate, e.g. before confirm/save
            product_lines = self.order_line.filtered(lambda l: not l.display_type and l.product_id)

            # if there are no product lines yet (only section/note), do nothing
            if product_lines:
                missing = product_lines.filtered(lambda l: not l.delivery_date)
                if missing:
                    names = ", ".join(missing.mapped(lambda l: l.name or l.product_id.display_name))
                    raise UserError(
                        _("Please set the delivery date on all product lines: %s") % names
                    )
        return super(SaleOrder, self).action_confirm()

    # @api.constrains("client_order_ref")
    # def _check_client_order_ref(self):
    #     if self.client_order_ref and not self.client_order_ref.isdigit():
    #         raise ValidationError(_("The PO Reference must contain only digits."))

    def _check_quote_word_limit(self):
        for record in self:
            if record.quote_desc:
                word_count = len(record.quote_desc.strip().split())
                if word_count > 10:
                    raise ValidationError("Quote / Description cannot exceed 10 words.")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._check_quote_word_limit()
        return res

    def write(self, vals):
        res = super().write(vals)
        self._check_quote_word_limit()
        return res

    @api.depends("order_line.delivery_date")
    def _compute_commitment_date(self):
        for order in self:
            # filter out False/None values
            delivery_dates = [d for d in order.order_line.mapped("delivery_date") if d]
            if delivery_dates:
                order.commitment_date = min(delivery_dates)
            else:
                order.commitment_date = False

    def _prepare_invoice(self):
        """ Method for passing value from sale order to regular invoice. """
        res = super(SaleOrder, self)._prepare_invoice()
        return res





