from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("vat", "country_id")
    def _check_duplicate_vat(self):
        vat = self.vat
        country_id = self.country_id.id

        if vat and country_id:
            country = self.env["res.country"].browse(country_id)
            if country.code == "SA":
                domain = [("vat", "=", vat)]
                existing = self.env["res.partner"].search(domain, limit=1)
                if existing:
                    raise ValidationError(
                        _(
                            "A contact with VAT %s already exists for Saudi Arabia customer/vendor: %s"
                        )
                        % (vat, existing.name)
                    )
