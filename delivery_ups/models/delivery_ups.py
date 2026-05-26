from odoo import api, models, fields, _
from odoo.exceptions import UserError
from .ups_request import UPSRequestCustom

class ProviderUPS(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('ups', "UPS")
    ], ondelete={'ups': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    ups_shipper_number = fields.Char(string='UPS Account Number', groups="base.group_system")
    ups_client_id = fields.Char(string='UPS Client ID', groups="base.group_system")
    ups_client_secret = fields.Char(string='UPS Client Secret', groups="base.group_system")
    ups_default_packaging_id = fields.Many2one('stock.package.type', string='UPS Package Type')
    ups_default_service_type = fields.Selection([
        ('03', 'UPS Ground'),
        ('11', 'UPS Standard'),
        ('01', 'UPS Next Day Air'),
        ('14', 'UPS Next Day Air Early'),
        ('13', 'UPS Next Day Air Saver'),
        ('02', 'UPS 2nd Day Air'),
        ('59', 'UPS 2nd Day Air A.M.'),
        ('12', 'UPS 3 Day Select'),
        ('65', 'UPS Saver'),
        ('07', 'UPS Worldwide Express'),
        ('08', 'UPS Worldwide Expedited'),
        ('54', 'UPS Worldwide Express Plus'),
        ('96', 'UPS Worldwide Express Freight')
    ], string="UPS Service Type", default='03')
    
    ups_package_weight_unit = fields.Selection([('LBS', 'Pounds'), ('KGS', 'Kilograms')], default='LBS')
    ups_package_dimension_unit = fields.Selection([('IN', 'Inches'), ('CM', 'Centimeters')], default='IN')
    ups_label_file_type = fields.Selection([('GIF', 'PDF'), ('ZPL', 'ZPL'), ('EPL', 'EPL'), ('SPL', 'SPL')], default='GIF')
    
    ups_bill_my_account = fields.Boolean(string='Bill My Account')
    ups_duty_payment = fields.Selection([('SENDER', 'Sender'), ('RECIPIENT', 'Recipient')], default="RECIPIENT")
    ups_cod = fields.Boolean(string='Collect on Delivery')
    ups_saturday_delivery = fields.Boolean(string='UPS Saturday Delivery')
    ups_cod_funds_code = fields.Selection([
        ('0', "Check, Cashier's Check or MoneyOrder"),
        ('8', "Cashier's Check or MoneyOrder"),
    ], default='0')

    def _compute_can_generate_return(self):
        super()._compute_can_generate_return()
        for carrier in self.filtered(lambda c: c.delivery_type == 'ups'):
            carrier.can_generate_return = True

    def ups_rate_shipment(self, order):
        ups = UPSRequestCustom(self)
        packages = self._get_packages_from_order(order, self.ups_default_packaging_id)
        
        cod_info = None
        if self.ups_cod:
            cod_info = {
                'currency': order.currency_id.name,
                'monetary_value': order.amount_total,
                'funds_code': self.ups_cod_funds_code,
            }
            
        try:
            res = ups.get_rate(
                shipper=order.company_id.partner_id,
                ship_from=order.warehouse_id.partner_id,
                ship_to=order.partner_shipping_id,
                packages=packages,
                cod_info=cod_info
            )
            
            # Convert currency if needed
            price = res['price']
            if order.currency_id.name != res['currency_code']:
                quote_currency = self.env['res.currency'].search([('name', '=', res['currency_code'])], limit=1)
                if quote_currency:
                    price = quote_currency._convert(price, order.currency_id, order.company_id, order.date_order or fields.Date.today())
                
            if self.ups_bill_my_account and order.partner_ups_carrier_account:
                price = 0.0

            return {'success': True, 'price': price, 'error_message': False, 'warning_message': False}
        except UserError as e:
            return {'success': False, 'price': 0.0, 'error_message': str(e), 'warning_message': False}

    def ups_send_shipping(self, pickings):
        res = []
        ups = UPSRequestCustom(self)
        for picking in pickings:
            packages = self._get_packages_from_picking(picking, self.ups_default_packaging_id)
            shipment_info = {
                'description': picking.origin or picking.name,
            }
            
            cod_info = None
            if self.ups_cod and picking.sale_id:
                cod_info = {
                    'currency': picking.sale_id.currency_id.name or picking.company_id.currency_id.name,
                    'monetary_value': picking.sale_id.amount_total,
                    'funds_code': self.ups_cod_funds_code,
                }

            result = ups.send_shipping(
                shipment_info=shipment_info,
                packages=packages,
                shipper=picking.company_id.partner_id,
                ship_from=picking.picking_type_id.warehouse_id.partner_id,
                ship_to=picking.partner_id,
                cod_info=cod_info
            )
            
            # Save attachments
            attachments = []
            for track_num, label_data in result['labels']:
                ext = 'pdf' if self.ups_label_file_type == 'GIF' else self.ups_label_file_type.lower()
                attachments.append((f"LabelUPS-{track_num}.{ext}", label_data))
                
            msg = _("Shipment created into UPS<br/><b>Tracking Number:</b> %s") % result['tracking_ref']
            picking.message_post(body=msg, attachments=attachments)
            
            # Currency conversion
            price = result['price']
            currency_order = picking.sale_id.currency_id if picking.sale_id else picking.company_id.currency_id
            if currency_order and currency_order.name != result['currency_code']:
                quote_currency = self.env['res.currency'].search([('name', '=', result['currency_code'])], limit=1)
                if quote_currency:
                    price = quote_currency._convert(price, currency_order, picking.company_id, fields.Date.today())

            res.append({
                'exact_price': price,
                'tracking_number': result['tracking_ref']
            })
        return res

    def ups_get_tracking_link(self, picking):
        return f'http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums={picking.carrier_tracking_ref}'

    def ups_cancel_shipment(self, picking):
        ups = UPSRequestCustom(self)
        ups.void_shipment(picking.carrier_tracking_ref)
        picking.message_post(body=_("Shipment %s has been cancelled.") % picking.carrier_tracking_ref)
        picking.write({'carrier_tracking_ref': '', 'carrier_price': 0.0})

    def ups_get_return_label(self, picking, tracking_number=None, origin_date=None):
        res = []
        ups = UPSRequestCustom(self)
        packages = self._get_packages_from_picking(picking, self.ups_default_packaging_id)
        
        shipment_info = {
            'description': picking.origin or picking.name,
        }
        
        result = ups.send_shipping(
            shipment_info=shipment_info,
            packages=packages,
            shipper=picking.company_id.partner_id,
            ship_from=picking.partner_id,
            ship_to=picking.picking_type_id.warehouse_id.partner_id,
            is_return=True
        )
        
        attachments = []
        for track_num, label_data in result['labels']:
            ext = 'pdf' if self.ups_label_file_type == 'GIF' else self.ups_label_file_type.lower()
            attachments.append((f"ReturnLabelUPS-{track_num}.{ext}", label_data))
            
        msg = _("Return label generated<br/><b>Tracking Number:</b> %s") % result['tracking_ref']
        picking.message_post(body=msg, attachments=attachments)
        
        # Currency conversion
        price = result['price']
        currency_order = picking.sale_id.currency_id if picking.sale_id else picking.company_id.currency_id
        if currency_order and currency_order.name != result['currency_code']:
            quote_currency = self.env['res.currency'].search([('name', '=', result['currency_code'])], limit=1)
            if quote_currency:
                price = quote_currency._convert(price, currency_order, picking.company_id, fields.Date.today())

        res.append({
            'exact_price': price,
            'tracking_number': result['tracking_ref']
        })
        return res
