# -*- coding: utf-8 -*-
from openerp import http

# class MyQuotation(http.Controller):
#     @http.route('/my_quotation/my_quotation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_quotation/my_quotation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_quotation.listing', {
#             'root': '/my_quotation/my_quotation',
#             'objects': http.request.env['my_quotation.my_quotation'].search([]),
#         })

#     @http.route('/my_quotation/my_quotation/objects/<model("my_quotation.my_quotation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_quotation.object', {
#             'object': obj
#         })