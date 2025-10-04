from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for record in self:
            partner = record.partner_id

            missing_fields = []
            if not partner.name_lang2:
                missing_fields.append('Name')
            if not partner.street1_lang2:
                missing_fields.append('Street 1')
            if not partner.street2_lang2:
                missing_fields.append('Street 2')
            if not partner.city_lang2:
                missing_fields.append('City')
            if not partner.country_lang2:
                missing_fields.append('Country')


            warn_fields = []
            if not partner.phone:
                warn_fields.append('Phone')
            if not partner.email:
                warn_fields.append('Email')
            if not partner.street:
                warn_fields.append('Street')
            if not partner.street2:
                warn_fields.append('Street 2')
            if not partner.city:
                warn_fields.append('City')
            if not partner.state_id:
                warn_fields.append('State')
            if not partner.zip:
                warn_fields.append('ZIP')
            if not partner.country_id:
                warn_fields.append('Country')

            if record.move_type == 'out_invoice' and (missing_fields or warn_fields):
                error_messages = []

                if missing_fields:
                    error_messages.append(
                        "You cannot confirm this invoice because the following Arabic fields are missing on the partner:\n- %s" % "\n- ".join(missing_fields)
                    )

                if warn_fields:
                    error_messages.append(
                        "You cannot confirm this bill because the following fields are missing on the partner:\n- %s" % "\n- ".join(warn_fields)
                    )

                if error_messages:
                    raise ValidationError("\n\n".join(error_messages))

            if record.move_type == 'in_invoice' and warn_fields:
                # Log a warning to the chatter (not blocking, not popup)
               raise ValidationError(
                    "You cannot confirm this bill because the following fields "
                    "are missing on the partner:\n- %s" % "\n- ".join(warn_fields))

        return super().action_post()


