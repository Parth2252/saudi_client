import logging
import requests
from odoo import models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_dhl_parcel_shipping_provider = fields.Boolean(string="Are You Using DHL Parcel?",
                                                      help="True when we need to use Dhl-Parcel shipping provider",
                                                      default=False, copy=False)
    dhl_parcel_api_url = fields.Char(string='Dhl-Parcel API URL',
                                     default="",
                                     help="Get Api-Url details from Dhl-Parcel website")
    dhl_parcel_api_key = fields.Char(string="Dhl-parcel api key",
                                     help="Get Api-Key details from Dhl-Parcel website")
    dhl_parcel_username = fields.Char(string='Dhl-parcel Username',
                                      help="")
    dhl_parcel_password = fields.Char(string="Dhl-parcel Password",
                                      help="")
    authentication_token = fields.Char(string="Dhl-parcel AuthenticationToken",
                                       help="", readonly=True)

    def generate_refresh_token_using_cron(self, ):
        for credential_id in self.search([]):
            try:
                if credential_id.use_dhl_parcel_shipping_provider:
                    credential_id.generate_authentication_token()
            except Exception as e:
                _logger.info("Getting an error in Generate Token request Odoo to Dhl Parcel: {0}".format(e))

    def generate_authentication_token(self):
        api_url = "%s/gateway/SSOAuthenticationAPI/1.0/ssoAuth/users/authenticate?username=%s&password=%s" % (
            self.dhl_parcel_api_url, self.dhl_parcel_username, self.dhl_parcel_password)
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.dhl_parcel_api_key
        }
        try:
            response_body = requests.get(url=api_url, headers=headers)
        except Exception as e:
            raise ValidationError(e)
        if response_body.status_code in [200, 201]:
            response_data = response_body.json()
            for data in response_data:
                self.authentication_token = data.get('authenticationToken')
            return True
        else:
            raise ValidationError(_(response_body.text))
