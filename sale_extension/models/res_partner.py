from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

import re


class ResPartner(models.Model):
    _inherit = "res.partner"

    beneficiary_country = fields.Many2one("res.country", string="Beneficiary Country")

    beneficiary_currency_id = fields.Many2one(
        "res.currency", string="Beneficiary Currency"
    )

    account_number = fields.Char("Account Number")
    beneficiary_bank_name = fields.Char("Bank Name")
    bank_city = fields.Char("Bank City")
    swift_code = fields.Char("Swift Code")
    beneficiary_full_name = fields.Char("Full Name")
    beneficiary_short_name = fields.Char("Short Name")
    beneficiary_address = fields.Text("Address")
    beneficiary_city = fields.Char("Beneficiary City")
    postal_code = fields.Char("Postal Code")

    # Added new fields(For the legal documents).
    cr_document = fields.Binary(string="CR Document", copy=False)
    cr_expire_date = fields.Date(string="CR Document Expire Date", copy=False)

    national_address_document = fields.Binary(
        string="National Address Certificate", copy=False
    )
    national_certificate_expire_date = fields.Date(
        string="National Certificate Expire Date", copy=False
    )

    vat_certificate_document = fields.Binary(string="VAT Certificate", copy=False)

    bank_latter_document = fields.Binary(string="Bank Latter", copy=False)
    iban_number = fields.Char(copy=False, string="IBAN Number")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        saudi_arabia = self.env.ref("base.sa", raise_if_not_found=False)
        if saudi_arabia:
            res["beneficiary_country"] = saudi_arabia.id

        sar_currency = self.env["res.currency"].search([("name", "=", "SAR")], limit=1)
        if sar_currency:
            res["beneficiary_currency_id"] = sar_currency.id

        return res

    # @api.constrains('customer_rank', 'supplier_rank')
    # def _check_customer_or_supplier(self):
    #     for rec in self:
    #         if not rec.customer_rank and not rec.supplier_rank:
    #             raise ValidationError("Contact must be marked as Customer or Supplier.")

    # @api.constrains("website")
    # def _check_website_characters(self):
    #     for partner in self:
    #         if partner.website:
    #             # Allow only alphabets (a-z, A-Z), dot (.) and dash (-)
    #             if not re.match(r"^[A-Za-z.\-]+$", partner.website):
    #                 raise ValidationError(
    #                     "Invalid website address for partner. "
    #                     "Only alphabets, '.' and '-' are allowed. Numbers and other special characters are not permitted."
    #                 )

    def action_preview_cr_document(self):
        """Preview the CR document inline (no forced download)"""
        self.ensure_one()
        if not self.cr_document:
            raise UserError("No CR Document uploaded.")
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/cr_document?download=false",
            "target": "new",
        }

    def action_preview_vat_certificate_document(self):
        """Preview the vat_certificate_document inline (no forced download)"""
        self.ensure_one()
        if not self.vat_certificate_document:
            raise UserError("No VAT Certificate Document uploaded.")
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/vat_certificate_document?download=false",
            "target": "new",
        }

    def action_preview_national_address_document(self):
        """Preview the CR document inline (no forced download)"""
        self.ensure_one()
        if not self.cr_document:
            raise UserError("No National Address Document uploaded.")
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/cr_document?download=false",
            "target": "new",
        }

    def action_preview_bank_latter_document(self):
        """Preview the CR document inline (no forced download)"""
        self.ensure_one()
        if not self.bank_latter_document:
            raise UserError("No Bank Later Document uploaded.")
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/bank_latter_document?download=false",
            "target": "new",
        }

    # @api.constrains(
    #     "country_id",
    #     "cr_document",
    #     "cr_expire_date",
    #     "national_address_document",
    #     "national_certificate_expire_date",
    # )
    # def _check_saudi_required_documents(self):
    #     if self.env.context.get("skip_saudi_document_check"):
    #         return

    #     for rec in self:
    #         if rec.country_id and rec.country_id.code == "SA":  # Saudi Arabia
    #             missing_fields = []
    #             if not rec.cr_document:
    #                 missing_fields.append("CR Document")
    #             if not rec.national_address_document:
    #                 missing_fields.append("National Address Certificate")

    #             if missing_fields:
    #                 raise ValidationError(
    #                     "The following documents are required for Saudi Arabia:\n%s"
    #                     % "\n".join(missing_fields)
    #                 )

    def copy(self, default=None):
        return super(
            ResPartner, self.with_context(skip_saudi_document_check=True)
        ).copy(default)
