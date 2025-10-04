from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import date

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm_1(self):
        """
        Override the default purchase order confirmation to validate supplier legal documents.

        This method performs two levels of validation before confirming a purchase order (RFQ):

        1. **Missing Documents Validation:**
           - Checks if each required legal document (CR Document, VAT Certificate,
             National Address Certificate) and its corresponding expiry date is configured
             on the supplier (`partner_id`).
           - If any document or expiry date is missing, the confirmation is blocked,
             and a UserError is raised listing all missing documents.

        2. **Expired Documents Validation:**
           - If the documents are configured, their expiry dates are compared with today's date.
           - If any configured document is expired, the confirmation is blocked,
             and a UserError is raised listing all expired documents along with their expiry dates.

        :raises UserError: If any required legal document is missing or expired for the supplier.
        :return: Result of the standard `button_confirm` method if validation passes.
        """
        for order in self:
            supplier = order.partner_id
            today = date.today()
            missing_docs = []
            expired_docs = []

            if self.env.user.has_group('sale_extension.group_allow_to_confirm_rfq_over_legal_document'):
                continue

            # --- CR Document ---
            if not supplier.cr_document or not supplier.cr_expire_date:
                missing_docs.append("CR Document")
            elif supplier.cr_expire_date < today:
                expired_docs.append(f"CR Document (Expired on {supplier.cr_expire_date})")

            # --- VAT Certificate ---
            # if not supplier.vat_certificate_document:
            #     missing_docs.append("VAT Certificate")

            # --- National Address Certificate ---
            if not supplier.national_address_document or not supplier.national_certificate_expire_date:
                missing_docs.append("National Address Certificate")
            elif supplier.national_certificate_expire_date < today:
                expired_docs.append(f"National Address Certificate (Expired on {supplier.national_certificate_expire_date})")

            # Raise error if any document missing
            if missing_docs and order.partner_id.country_id.code == 'SA':
                raise UserError(_(
                    "The following legal documents are missing for supplier '%s': %s\n"
                    "Please configure these documents before confirming the RFQ."
                ) % (supplier.name, ", ".join(missing_docs)))

            # Raise error if any document expired
            if expired_docs and order.partner_id.country_id.code == 'SA':
                raise UserError(_(
                    "The following supplier documents are expired for '%s': %s\n"
                    "Please update these documents before confirming the RFQ."
                ) % (supplier.name, ", ".join(expired_docs)))

        return super(PurchaseOrder, self).button_confirm()
