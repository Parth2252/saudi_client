import json
import base64
from contextlib import contextmanager
from unittest.mock import patch
import requests

from odoo.tests.common import TransactionCase, Form, tagged
from odoo import Command

@contextmanager
def _mock_ups_request(currency_code='USD'):
    def _mock_request(*args, **kwargs):
        url = kwargs.get('url') or next((a for a in args if isinstance(a, str) and 'http' in a), '')
        response = requests.Response()
        response.status_code = 200
        response.encoding = 'utf-8'
        
        if 'oauth/token' in url:
            response._content = json.dumps({'access_token': 'mock_token'}).encode()
        elif '/Rate' in url:
            response._content = json.dumps({
                'RateResponse': {
                    'RatedShipment': {
                        'TotalCharges': {'MonetaryValue': '15.50', 'CurrencyCode': currency_code}
                    }
                }
            }).encode()
        elif url.endswith('/ship'):
            img_b64 = base64.b64encode(b'mock_image_data').decode('utf-8')
            response._content = json.dumps({
                'ShipmentResponse': {
                    'ShipmentResults': {
                        'ShipmentIdentificationNumber': '1Z999999999',
                        'ShipmentCharges': {'TotalCharges': {'MonetaryValue': '15.50', 'CurrencyCode': currency_code}},
                        'PackageResults': {
                            'TrackingNumber': '1Z999999999',
                            'ShippingLabel': {'GraphicImage': img_b64}
                        }
                    }
                }
            }).encode()
        elif '/void/cancel' in url:
            response._content = json.dumps({
                'VoidShipmentResponse': {
                    'SummaryResult': {
                        'Status': {'Description': 'Voided successfully'}
                    }
                }
            }).encode()
        else:
            response.status_code = 404
            response._content = b'Not Found'
            
        return response

    with patch.object(requests.Session, 'request', _mock_request):
        yield

@tagged('post_install', '-at_install')
class TestDeliveryUPS(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.company_partner = cls.env.company.partner_id
        cls.company_partner.write({
            'country_id': cls.env.ref('base.us').id,
            'state_id': cls.env.ref('base.state_us_5').id,
            'city': 'San Francisco',
            'street': 'Market St',
            'phone': '1234567890',
            'zip': '94103',
        })
        
        cls.customer = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'country_id': cls.env.ref('base.us').id,
            'state_id': cls.env.ref('base.state_us_5').id,
            'city': 'Los Angeles',
            'street': 'Sunset Blvd',
            'phone': '0987654321',
            'zip': '90001',
        })
        
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
            'weight': 5.0,
            'seller_ids': [Command.create({
                'partner_id': cls.company_partner.id,
                'min_qty': 1.0,
                'price': 5.0,
            })]
        })
        
        cls.packaging = cls.env['stock.package.type'].create({
            'name': 'Custom Box',
            'package_carrier_type': 'ups',
            'shipper_package_code': '02',
        })
        
        cls.carrier = cls.env['delivery.carrier'].create({
            'name': 'UPS Carrier Custom',
            'delivery_type': 'ups',
            'ups_shipper_number': '123456',
            'ups_client_id': 'mock_client_id',
            'ups_client_secret': 'mock_client_secret',
            'ups_default_packaging_id': cls.packaging.id,
            'ups_default_service_type': '03',
            'ups_label_file_type': 'ZPL',
            'product_id': cls.env['product.product'].create({'name': 'UPS Delivery', 'type': 'service'}).id,
        })

    def test_ups_rate_and_ship(self):
        payment_term = self.env['account.payment.term'].search([], limit=1)
        if not payment_term:
            payment_term = self.env['account.payment.term'].create({'name': 'Immediate Payment'})
            
        incoterm = self.env['account.incoterms'].search([], limit=1)
        if not incoterm:
            incoterm = self.env['account.incoterms'].create({'name': 'Test Incoterm', 'code': 'TST'})
            
        order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'client_order_ref': 'PO-12345',
            'payment_term_id': payment_term.id,
            'incoterm': incoterm.id,
            'incoterm_location': 'Test Location',
            'quote_desc': 'Test Quote',
            'order_line': [Command.create({
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'price_unit': 10.0,
                'delivery_date': '2026-12-31',
                'vendor_price': 8.0,
            })]
        })
        
        with _mock_ups_request(currency_code=order.currency_id.name):
            res = self.carrier.ups_rate_shipment(order)
            self.assertTrue(res['success'])
            self.assertEqual(res['price'], 15.50)
            
            order.carrier_id = self.carrier
            order.action_confirm()
            
            picking = order.picking_ids[0]
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
            picking.button_validate()
            
            self.assertEqual(picking.carrier_tracking_ref, '1Z999999999')
            self.assertEqual(picking.carrier_price, 15.50)
            
            # Test Cancel
            picking.cancel_shipment()
            self.assertFalse(picking.carrier_tracking_ref)
