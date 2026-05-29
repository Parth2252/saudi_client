import base64
import io
import re
import requests
import PIL.PdfImagePlugin  # pylint: disable=W0611
from PIL import Image

from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_repr

TEST_BASE_URL = "https://wwwcie.ups.com"
PROD_BASE_URL = "https://onlinetools.ups.com"
API_VERSION = "v1"

class UPSRequestCustom:
    def __init__(self, carrier):
        self.carrier = carrier.sudo()
        self.logger = self.carrier.log_xml
        self.base_url = PROD_BASE_URL if self.carrier.prod_environment else TEST_BASE_URL
        self.client_id = self.carrier.ups_client_id
        self.client_secret = self.carrier.ups_client_secret
        self.shipper_number = self.carrier.ups_shipper_number
        self.session = requests.Session()

    def _get_access_token(self):
        if not self.client_id or not self.client_secret:
            raise ValidationError(_("UPS Client ID and Client Secret are required."))
        
        url = f"{self.base_url}/security/v1/oauth/token"
        headers = {'x-merchant-id': self.client_id}
        data = {"grant_type": "client_credentials"}
        
        try:
            res = self.session.post(url, data=data, headers=headers, auth=(self.client_id, self.client_secret), timeout=15)
            self.logger(f"POST {url}\n{res.status_code}\n{res.text}", "ups oauth request")
            res.raise_for_status()
            res_data = res.json()
            return res_data.get('access_token')
        except Exception as e:
            self.logger(str(e), "ups oauth error")
            raise ValidationError(_("Could not authenticate with UPS. Please check your Client ID and Client Secret."))

    def _send_request(self, endpoint, method='POST', json_data=None):
        access_token = self._get_access_token()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        self.logger(f"{method} {url}\n{json_data}", "ups api request")
        import json
        print(f"\n--- API REQUEST TO {url} ---")
        print(json.dumps(json_data, indent=2))
        try:
            res = self.session.request(method=method, url=url, json=json_data, headers=headers, timeout=15)
            self.logger(f"{res.status_code}\n{res.text}", "ups api response")
            print(f"\n--- API RESPONSE ---")
            print(f"{res.status_code}\n{res.text}\n----------------------------")
        except requests.exceptions.RequestException as e:
            self.logger(str(e), "ups api connection error")
            raise ValidationError(_("Connection error with UPS API: %s") % e)
        
        try:
            res_json = res.json()
        except Exception:
            raise ValidationError(_("Failed to decode UPS response."))
            
        if not res.ok:
            error_msg = self._parse_errors(res_json)
            raise ValidationError(error_msg)
            
        return res_json

    def _parse_errors(self, res_json):
        errors = []
        if 'response' in res_json and 'errors' in res_json['response']:
            for err in res_json['response']['errors']:
                errors.append(err.get('message', 'Unknown Error'))
        return "UPS Error: " + ", ".join(errors) if errors else "Unknown UPS Error"

    def _clean_phone(self, phone):
        return re.sub(r'[^0-9]', '', phone or '')

    def _format_address(self, partner, is_shipper=False):
        address = {
            'AddressLine': [partner.street or '', partner.street2 or ''],
            'City': partner.city or '',
            'PostalCode': partner.zip or '',
            'CountryCode': partner.country_id.code or '',
            'StateProvinceCode': partner.state_id.code or '',
        }
        res = {
            'Name': (partner.name or '')[:35],
            'AttentionName': (partner.name or '')[:35],
            'Address': address,
            'Phone': {'Number': self._clean_phone(partner.phone or partner.mobile)[:15]},
        }
        if partner.email:
            res['EMailAddress'] = partner.email[:50]
        if is_shipper and self.shipper_number:
            res['ShipperNumber'] = self.shipper_number
        return res

    def _build_packages(self, packages, cod_info=None):
        pkg_data = []
        for p in packages:
            desc = ','.join([c.product_id.name for c in p.commodities])
            if not desc:
                desc = 'UPS Shipment'
            desc = re.sub(r'[^\w\s]', '', desc)[:35]
            
            weight = sum(c.qty * c.product_id.weight for c in p.commodities) or p.weight or 0.1
            if self.carrier.ups_package_weight_unit == 'KGS':
                weight = weight # assuming product weights are in KG
            elif self.carrier.ups_package_weight_unit == 'LBS':
                weight = weight * 2.20462
            
            pkg = {
                'PackagingType': {'Code': p.packaging_type or '02'},
                'Packaging': {'Code': p.packaging_type or '02'},
                'Description': desc,
                'PackageWeight': {
                    'UnitOfMeasurement': {'Code': self.carrier.ups_package_weight_unit},
                    'Weight': f"{weight:.2f}"
                }
            }
            if p.dimension:
                pkg['Dimensions'] = {
                    'UnitOfMeasurement': {'Code': self.carrier.ups_package_dimension_unit},
                    'Length': str(p.dimension.get('length', '')),
                    'Width': str(p.dimension.get('width', '')),
                    'Height': str(p.dimension.get('height', '')),
                }
            
            if cod_info:
                pkg['PackageServiceOptions'] = {
                    'COD': {
                        'CODFundsCode': cod_info['funds_code'],
                        'CODAmount': {
                            'MonetaryValue': f"{cod_info['monetary_value']:.2f}",
                            'CurrencyCode': cod_info['currency']
                        }
                    }
                }
            pkg_data.append(pkg)
        return pkg_data

    def get_rate(self, shipper, ship_from, ship_to, packages, cod_info=None):
        data = {
            "RateRequest": {
                "Request": {"RequestOption": "Rate"},
                "Shipment": {
                    "Shipper": self._format_address(shipper, is_shipper=True),
                    "ShipFrom": self._format_address(ship_from),
                    "ShipTo": self._format_address(ship_to),
                    "Service": {"Code": self.carrier.ups_default_service_type},
                    "Package": self._build_packages(packages, cod_info),
                    "ShipmentRatingOptions": {"NegotiatedRatesIndicator": "1"}
                }
            }
        }
        res = self._send_request(f"/api/rating/{API_VERSION}/Rate", method='POST', json_data=data)
        
        try:
            rate_shipment = res['RateResponse']['RatedShipment']
            # Fallback to TotalCharges if negotiated rates missing
            charge = rate_shipment.get('NegotiatedRateCharges', {}).get('TotalCharge') or rate_shipment['TotalCharges']
            return {
                'currency_code': charge['CurrencyCode'],
                'price': float(charge['MonetaryValue'])
            }
        except KeyError:
            raise ValidationError(_("Could not parse UPS Rate Response."))

    def send_shipping(self, shipment_info, packages, shipper, ship_from, ship_to, cod_info=None, is_return=False):
        payment_info = {
            'ShipmentCharge': [{
                'Type': '01',
                'BillShipper': {'AccountNumber': self.shipper_number}
            }]
        }
        
        if self.carrier.ups_duty_payment == 'SENDER':
            payment_info['ShipmentCharge'].append({
                'Type': '02',
                'BillShipper': {'AccountNumber': self.shipper_number}
            })

        shipment = {
            "Description": shipment_info.get('description')[:35],
            "Shipper": self._format_address(shipper, is_shipper=True),
            "ShipFrom": self._format_address(ship_from),
            "ShipTo": self._format_address(ship_to),
            "Service": {"Code": self.carrier.ups_default_service_type},
            "Package": self._build_packages(packages, cod_info),
            "PaymentInformation": payment_info,
            "ShipmentRatingOptions": {"NegotiatedRatesIndicator": "1"}
        }

        if is_return:
            shipment['ReturnService'] = {'Code': '9'}

        data = {
            "ShipmentRequest": {
                "Request": {"RequestOption": "nonvalidate"},
                "LabelSpecification": {
                    "LabelImageFormat": {"Code": self.carrier.ups_label_file_type},
                },
                "Shipment": shipment
            }
        }
        
        res = self._send_request(f"/api/shipments/{API_VERSION}/ship", method='POST', json_data=data)
        
        try:
            result = res['ShipmentResponse']['ShipmentResults']
            tracking_num = result['ShipmentIdentificationNumber']
            
            packs = result.get('PackageResults', [])
            if not isinstance(packs, list):
                packs = [packs]
                
            labels = []
            for pack in packs:
                img_data = pack['ShippingLabel']['GraphicImage']
                labels.append((pack['TrackingNumber'], self._convert_label(img_data)))
                
            charge = result.get('NegotiatedRateCharges', {}).get('TotalCharge') or result['ShipmentCharges']['TotalCharges']
            
            return {
                'tracking_ref': tracking_num,
                'labels': labels,
                'currency_code': charge['CurrencyCode'],
                'price': float(charge['MonetaryValue'])
            }
        except KeyError:
            raise ValidationError(_("Could not parse UPS Ship Response."))

    def void_shipment(self, tracking_ref):
        res = self._send_request(f"/api/shipments/{API_VERSION}/void/cancel/{tracking_ref}", method='DELETE')
        try:
            return res['VoidShipmentResponse']['SummaryResult']['Status']['Description']
        except KeyError:
            raise ValidationError(_("Could not parse UPS Void Response."))

    def _convert_label(self, image_b64):
        decoded = base64.b64decode(image_b64)
        if self.carrier.ups_label_file_type == 'GIF':
            # Convert GIF to PDF
            img = Image.open(io.BytesIO(decoded))
            out = io.BytesIO()
            img.save(out, 'PDF')
            return out.getvalue()
        return decoded
