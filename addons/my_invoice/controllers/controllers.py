# -*- coding: utf-8 -*-
from openerp import http

# class MyInvoice(http.Controller):
#     @http.route('/my_invoice/my_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_invoice/my_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_invoice.listing', {
#             'root': '/my_invoice/my_invoice',
#             'objects': http.request.env['my_invoice.my_invoice'].search([]),
#         })

#     @http.route('/my_invoice/my_invoice/objects/<model("my_invoice.my_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_invoice.object', {
#             'object': obj
#         })