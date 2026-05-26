from odoo import models, fields, _
from odoo.exceptions import ValidationError
import datetime
from requests import request
import json
import binascii
import logging
_logger = logging.getLogger("DHL Parcel")


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    delivery_type = fields.Selection(selection_add=[("dhl_parcel_vts", "DHL Parcel")],ondelete={'dhl_parcel_vts': 'set default'})

    package_id = fields.Many2one('stock.package.type', string="Default Package", help="please select package type")

    dhl_parcel_label_format = fields.Selection([('PNG6x4', 'PNG 6x4'),
                                                ('ZPL200dpi6x4', 'ZPL 6x4'),
                                                ('PDF200dpi6x4', 'PDF 6x4')],
                                               string="Dhl Parcel Label Format",
                                               help="Paper format given by Dhl Parcel.")

    closed_for_lunch = fields.Boolean(string="Closed For Lunch", default=False)

    dhl_parcel_service_code = fields.Selection(
        [
            # parcels(YYY)
            ('1', '1 - Next Day -  if receiver not at home then product deliver to neighbour'),
            ('2', '2 - Next Day 12:00 - if receiver not at home then product deliver to neighbour'),
            ('9', '9 - Next Day 10:30 - if receiver not at home then product deliver to neighbour'),
            ('4', '4 - Saturday - if receiver not at home then product deliver to neighbour'),
            ('7', '7 - Saturday 10:30 - if receiver not at home then product deliver to neighbour'),
            ('48', '48 - 48 hrs - if receiver not at home then product deliver to neighbour'),
            # (NYN)
            ('220', '220 - Next Day - Deliver to only Receiver'),
            ('221', '221 - Next Day 12:00 - Deliver to only Receiver'),
            ('222', '222 - Next Day 10:30 - Deliver to only Receiver'),
            ('3', '3 - Next Day 09:00 - Deliver to only Receiver'),
            ('225', '225 - Saturday - Deliver to only Receiver'),
            ('226', '226 - Saturday 10:30 - Deliver to only Receiver'),
            ('5', '5 - Saturday 09:00 - Deliver to only Receiver'),
            # (YYY/Safe)
            ('210', '210 - Next Day  - Leave Safe if receiver not at home'),
            ('211', '211- Next Day 12:00  - Leave Safe if receiver not at home'),
            ('212', '212 - Next Day 10:30  - Leave Safe if receiver not at home'),
            ('215', '215 - Saturday  - Leave Safe if receiver not at home'),
            ('216', '216 - Saturday 10:30  - Leave Safe if receiver not at home'),
            ('72', '72 - 48 Hr - Leave Safe if receiver not at home'),
            ('72', '72 - 48 Hr + (used for 72h areas) - Leave Safe if receiver not at home'),

            # pallets(NYN)
            ('97', '97 - Pallet 24hrs - Deliver to only Receiver'),
            ('98', '98 - Pallet 48hrs - Deliver to only Receiver'),

            # send to 3rd party(NYN)
            ('451', '451 - Next Day - Deliver to only Receiver'),
            ('452', '452 - Next Day 12:00 - Deliver to only Receiver'),
            ('459', '459 - Next Day 10:30 - Deliver to only Receiver'),
            ('453', '453 - Next Day 09:00 - Deliver to only Receiver'),
            ('454', '454 - saturday  - Deliver to only Receiver'),

            # international(NYN)
            ('101', '101 - Worldwide Air - Deliver to only Receiver'),
            ('102', '102 - DHL Parcel International - Deliver to only Receiver'),
            ('204', '204 - International Road Economy - Deliver to only Receiver'),
            ('206', '206 - DHL Parcel Connect - Deliver to only Receiver'),

            # Bagit Small 1kg(yyy)
            ('40', '40 - Next Day -  if receiver not at home then product deliver to neighbour'),
            ('41', '41 - Next Day 12:00 - if receiver not at home then product deliver to neighbour'),
            ('49', '49 - Next Day 10:30 - if receiver not at home then product deliver to neighbour'),
            ('43', '43 - Saturday - if receiver not at home then product deliver to neighbour'),
            ('46', '46 - Saturday 10:30 - if receiver not at home then product deliver to neighbour'),

            # NYN
            ('240', '240 - Next Day - Deliver to only Receiver'),
            ('241', '241 - Next Day 12:00 - Deliver to only Receiver'),
            ('242', '242 - Next Day 10:30 - Deliver to only Receiver'),
            ('42', '42 - Next Day 09:00 - Deliver to only Receiver'),
            ('245', '245 - Saturday - Deliver to only Receiver'),
            ('246', '246 - Saturday 10:30 - Deliver to only Receiver'),
            ('44', '44 - Saturday 09:00 - Deliver to only Receiver'),

            # YYY/Safe
            ('230', '230 - Next Day - Leave Safe if receiver not at home'),
            ('231', '231 - Next Day 12:00 - Leave Safe if receiver not at home'),
            ('232', '232 - Next Day 10:30 - Leave Safe if receiver not at home'),
            ('235', '235 - Saturday - Leave Safe if receiver not at home'),
            ('236', '236 - Saturday 10:30 - Leave Safe if receiver not at home'),

            # Bagit Medium 2kg
            # YYY
            ('30', '30 - Next Day -  if receiver not at home then product deliver to neighbour'),
            ('31', '31 - Next Day 12:00 - if receiver not at home then product deliver to neighbour'),
            ('39', '39 - Next Day 10:30 - if receiver not at home then product deliver to neighbour'),
            ('33', '33 - Saturday - if receiver not at home then product deliver to neighbour'),
            ('36', '36 - Saturday 10:30 - if receiver not at home then product deliver to neighbour'),

            # NYN
            ('250', '250 - Next Day - Deliver to only Receiver'),
            ('251', '251 - Next Day 12:00 - Deliver to only Receiver'),
            ('252', '252 - Next Day 10:30 - Deliver to only Receiver'),
            ('32', '32 - Next Day 09:00 - Deliver to only Receiver'),
            ('255', '255 - Saturday - Deliver to only Receiver'),
            ('256', '256 - Saturday 10:30 - Deliver to only Receiver'),
            ('34', '34 - Saturday 09:00 - Deliver to only Receiver'),

            # Bagit Large 5kg
            # YYY
            ('20', '20 - Next Day -  if receiver not at home then product deliver to neighbour'),
            ('21', '21 - Next Day 12:00 - if receiver not at home then product deliver to neighbour'),
            ('29', '29 - Next Day 10:30 - if receiver not at home then product deliver to neighbour'),
            ('23', '23 - Saturday - if receiver not at home then product deliver to neighbour'),
            ('26', '26 - Saturday 10:30 - if receiver not at home then product deliver to neighbour'),

            # NYN
            ('260', '260 - Next Day - Deliver to only Receiver'),
            ('261', '261 - Next Day 12:00 - Deliver to only Receiver'),
            ('262', '262 - Next Day 10:30 - Deliver to only Receiver'),
            ('22', '22 - Next Day 09:00 - Deliver to only Receiver'),
            ('265', '265 - Saturday - Deliver to only Receiver'),
            ('266', '266 - Worldwide Air - Deliver to only Receiver'),
            ('24', '24 - Saturday 09:00 - Deliver to only Receiver'),

            # Bagit xl 10kg
            # YYY
            ('10', '10 - Next Day -  if receiver not at home then product deliver to neighbour'),
            ('11', '11 - Next Day 12:00 - if receiver not at home then product deliver to neighbour'),
            ('19', '19 - Next Day 10:30 - if receiver not at home then product deliver to neighbour'),
            ('13', '13 - Saturday - if receiver not at home then product deliver to neighbour'),
            ('16', '16 - Saturday 10:30 - if receiver not at home then product deliver to neighbour'),

            # NYN
            ('270', '270 - Next Day - Deliver to only Receiver'),
            ('271', '271 - Next Day 12:00 - Deliver to only Receiver'),
            ('272', '272 - Next Day 10:30 - Deliver to only Receiver'),
            ('12', '12 - Next Day 09:00 - Deliver to only Receiver'),
            ('275', '275 - Saturday - Deliver to only Receiver'),
            ('276', '276 - Worldwide Air - Deliver to only Receiver'),
            ('14', '14 - Saturday 09:00 - Deliver to only Receiver'),
        ], string="DHL Service")

    use_dhl_international_service = fields.Boolean(string="International Service")
    extend_cover_required = fields.Boolean(string="Extend Cover Required", help="If extended cover is required for "
                                                                                "this consignment then true otherwise"
                                                                                " false")
    dhl_invoice_required = fields.Boolean(string="Invoice Required", help="Invoice PDF required? Do you want DHL to "
                                                                          "return the invoice for you to print. Pass "
                                                                          "false if you are intending to provide your "
                                                                          "own commercial/proforma invoice")
    dhl_invoice_type = fields.Selection([('commercial', 'Commercial'), ('proforma', 'Proforma')], string="DHL Invoice "
                                                                                                         "Type ")
    dhl_terms_of_delivery = fields.Selection([('DAP', 'DAP (Delivery At Place)'), ('DDP', 'DDP (Delivered Duty Paid)')],
                                             string="DHL terms of delivery")
    dhl_reason_for_export = fields.Selection([('gift', 'Gift'), ('documents', 'Documents'), ('commercial sample', 'Commercial Sample'),
                                              ('returned goods', 'Returned Goods'), ('repairs', 'Repairs'), ('commercial sale', 'Commercial Sale')],
                                             string="Reason For Export")
    dhl_account_number = fields.Char(string="DHL Account Number")

    def dhl_parcel_vts_rate_shipment(self, order):
        return {'success': True, 'price': 0.0, 'error_message': False, 'warning_message': False}

    def dhl_parcel_request_method(self, pickings):
        """This Method is Used For Create A Request Data
            this Method Returns A collections of Request data"""
        parcels = []
        no_of_package = 0
        package_ids = pickings.move_line_ids.mapped('result_package_id')
        for package_id in package_ids:
            no_of_package = no_of_package + 1
            parcels.append(
                {
                    "length": package_id.package_type_id and package_id.package_type_id.packaging_length or 0,
                    "width": package_id.package_type_id and package_id.package_type_id.width or 0,
                    "height": package_id.package_type_id and package_id.package_type_id.height or 0,
                    "weight": package_id.shipping_weight or 0
                })
        if pickings.weight_bulk:
            no_of_package = no_of_package + 1
            parcels.append(
                {
                    "length": self.package_id and self.package_id.packaging_length or 0,
                    "width": self.package_id and self.package_id.width or 0,
                    "height": self.package_id and self.package_id.height or 0,
                    "weight": pickings.weight_bulk or 0
                })
        recipient_address = pickings.partner_id
        if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")
        #article
        article = []
        for order_line in pickings.sale_id.order_line.filtered(lambda order_line:order_line.is_delivery == False):
            article_data = {
                                "commodityCode": "{}".format(order_line and order_line.product_id.hs_code or " "),
                                "goodsDescription": order_line and order_line.product_id and order_line.product_id.name or "",
                                "quantity": int(order_line.product_qty or 0),
                                "unitValue": float(order_line.price_total or 0.0),
                                "unitWeight": order_line.product_id and order_line.product_id.weight or 0.0,
                                "countryofManufacture": recipient_address and recipient_address.country_id and recipient_address.country_id.country_iso_code or " "
                            }
            article.append(article_data)
        username = self.company_id and self.company_id.dhl_parcel_username
        password = self.company_id and self.company_id.authentication_token
        if not username and not password:
            raise ValidationError("Please Define DHL Username and Authentication Token in company")
        payload = {
            'userName': self.company_id and self.company_id.dhl_parcel_username or "",
            'authenticationToken': self.company_id and self.company_id.authentication_token or "",
            'accountNumber': self.dhl_account_number or "",
            'collectionInfo':
                {
                    'collectionJobNumber': pickings and pickings.collection_Job_Number or "",
                },
            'delivery': {
                'localContactName': "{}".format(recipient_address.name or ""),
                'localContactNumber': "{}".format(recipient_address.phone or ""),
                'contactNumberType': "mobile",
                'localContactEmail': "{}".format(recipient_address.email or ""),

                'deliveryAddresses': [
                    {
                        'addressType': 'doorstep',
                        'address1': "{}".format(recipient_address.street or ""),
                        'address2': "{}".format(recipient_address.street2 or ""),
                        'postalTown': "{}".format(recipient_address.city or ""),
                        'postcode': "{}".format(recipient_address.zip or ""),
                        'countryCode': "{}".format(
                            recipient_address.country_id and recipient_address.country_id.country_iso_code or ""),
                    }
                ]

            },
            'serviceKey': self.dhl_parcel_service_code,
            'items': no_of_package,
            'totalWeight': int(pickings and pickings.shipping_weight),
            'customerReference': pickings and pickings.origin,
            'parcels': parcels,
            "extendedCoverRequired": "{}".format(self.extend_cover_required),
            'recipient': {
                'contactName': "{}".format(recipient_address.name or ""),
                'contactEmail': "{}".format(recipient_address.email or ""),
                'contactNumber': "{}".format(recipient_address.mobile or ""),
                'recipientAddress': {
                    'businessName': "",
                    'addressType': 'business',
                    'address1': "{}".format(recipient_address.street or ""),
                    'address2': "{}".format(recipient_address.street2 or ""),
                    'postalTown': "{}".format(recipient_address.city or ""),
                    'county': "{}".format(recipient_address.country_id and recipient_address.country_id.code or ""),
                    'postcode': "{}".format(recipient_address.zip or ""),
                    'countryCode' : "{}".format(recipient_address.country_id and recipient_address.country_id.country_iso_code or " ")
                }
            },
            "InvoiceRequired": "{}".format(self.dhl_invoice_required),
            'labelFormat': "PDF200dpi6x4",
            "customsDeclaration": {
                "full": {
                    "invoiceType": self.dhl_invoice_type,
                    "InvoiceNumber" : pickings.name,
                    "InvoiceDate": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "articles": {
                        "article": article},
                    "totalArticles": len(article),
                    "shippingCharges": "0.00",
                    "totalValue": float(pickings.sale_id.amount_total),
                    "currencyCode": self.company_id and self.company_id.currency_id and self.company_id.currency_id.name,
                    "reasonforExport": self.dhl_reason_for_export,
                    "termsOfDelivery": self.dhl_terms_of_delivery,
                }}}
        if self.use_dhl_international_service:
            payload.get('delivery').get('deliveryAddresses')[0]['zipcode'] = \
                payload.get('delivery').get('deliveryAddresses')[0].pop('postcode')
            payload.get('recipient').get('recipientAddress')['zipcode'] = payload.get('recipient').get(
                'recipientAddress').pop('postcode')
        data = json.dumps(payload)
        return data

    def get_dhl_parcel_url_method(self, api_operation):
        if self.company_id and self.company_id.dhl_parcel_api_url:
            url = self.company_id.dhl_parcel_api_url + api_operation
            return url
        else:
            raise ValidationError(_("Set the appropriate URL in Company."))

    def get_collection_job_number(self, pickings):
        api_url = "%s/v1/collection/collectionrequests" % self.company_id.dhl_parcel_api_url
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': pickings.company_id and pickings.company_id.dhl_parcel_api_key
        }
        CurrentDate = datetime.datetime.now().date()
        scheduled_date = datetime.datetime.strptime(str(CurrentDate),"%Y-%m-%d")
        payload = {
            'userName': pickings.company_id and pickings.company_id.dhl_parcel_username,
            'authenticationToken': pickings.company_id and pickings.company_id.authentication_token,
            'accountNumber': self.dhl_account_number,
            'collectionDate': scheduled_date.strftime("%Y-%m-%d"),
            'closedForLunch': pickings.carrier_id and pickings.carrier_id.closed_for_lunch,
            'earliestTime': "09:00",
            'latestTime': "09:00"
        }
        data = json.dumps(payload)

        try:
            _logger.info(">>> Sending Post Request To {}".format(api_url))
            _logger.info(">>> Request Data  {}".format(data))
            response_body = request(method="POST", url=api_url, data=data, headers=headers)
            if response_body.status_code in [200, 201]:
                _logger.info(">>> Successfully  Response from {}".format(api_url))
                _logger.info(">>> Response Data {}".format(response_body.text))
                response_data = response_body.json()
                collection_number = response_data.get('collectionJobNumber')
                if not collection_number:
                    raise ValidationError(
                        _("can't create collection number, \n api url {} \n response data {}").format(api_url,
                                                                                                      response_data))
                else:
                    pickings.collection_Job_Number = collection_number
            else:
                raise ValidationError(response_body.text)
        except Exception as e:
            raise ValidationError(e)

    def dhl_parcel_vts_send_shipping(self, pickings):
        try:
            if not pickings.collection_Job_Number:
                self.get_collection_job_number(pickings)
                headers = {
                    'Content-Type': 'application/json',
                    'x-api-key': self.company_id and self.company_id.dhl_parcel_api_key
                }
                api_url = self.get_dhl_parcel_url_method(
                    "/gateway/DomesticConsignment/2.0/DomesticConsignment")
                if self.use_dhl_international_service:
                    api_url = self.get_dhl_parcel_url_method("/v3/internationalconsignment/internationalconsignment")
                request_data = self.dhl_parcel_request_method(pickings)
                _logger.info(">>>> Sending Post Request For Create Shipment URL {}".format(api_url))
                _logger.info(">>> Request Data For Create Shipment {}".format(request_data))
                response_body = request(method="POST", url=api_url, data=request_data, headers=headers)

                if response_body.status_code in [200, 201]:
                    _logger.info(">>> Successfully  Response from {}".format(api_url))
                    _logger.info(">>> Response Data {}".format(response_body.text))
                    response_body = response_body.json()
                    tracking_numbers = []
                    for identifier in response_body.get('identifiers'):
                        tracking_numbers.append(identifier.get('identifierValue'))
                    for label_data in response_body.get('labels'):
                        label_binary_data = binascii.a2b_base64(str(label_data))
                        message = (_("Shipment created!<br/> <b>Shipment Tracking Number : </b>%s") % tracking_numbers)
                        pickings.message_post(body=message, attachments=[
                            ('DHL Parcel-%s.%s' % (pickings.id, "pdf"), label_binary_data)])

                    response = []
                    shipping_data = {
                        'exact_price': 0.0,
                        'tracking_number': ','.join(tracking_numbers)}
                    response += [shipping_data]
                    return response
                else:
                    raise ValidationError(response_body.text)
            else:
                response = []
                shipping_data = {
                        'exact_price': 0.0,
                        'tracking_number': False}
                response += [shipping_data]
                return response
        except Exception as e:
            raise ValidationError(e)

    def dhl_parcel_vts_cancel_shipment(self, pickings):
        raise ValidationError("DHL Doesn't Provide Cancel API!")

    def dhl_parcel_vts_get_tracking_link(self, picking):
        res = "https://www.dhlparcel.nl/en/consumer/track-and-trace"
        return res