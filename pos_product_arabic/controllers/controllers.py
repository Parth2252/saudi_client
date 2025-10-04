# -*- coding: utf-8 -*-
from odoo import http

# class PosProductArabic(http.Controller):
#     @http.route('/pos_product_arabic/pos_product_arabic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_product_arabic/pos_product_arabic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_product_arabic.listing', {
#             'root': '/pos_product_arabic/pos_product_arabic',
#             'objects': http.request.env['pos_product_arabic.pos_product_arabic'].search([]),
#         })

#     @http.route('/pos_product_arabic/pos_product_arabic/objects/<model("pos_product_arabic.pos_product_arabic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_product_arabic.object', {
#             'object': obj
#         })