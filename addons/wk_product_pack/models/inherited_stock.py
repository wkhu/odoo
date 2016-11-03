# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging
from openerp.tools.float_utils import float_round
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)

class ProductTemplate(osv.osv):
	_inherit = 'product.template'

	def _product_available(self, cr, uid, ids, name, arg, context=None):
		prod_available = {}
		product_ids = self.browse(cr, uid, ids, context=context)
		var_ids = []
		for product in product_ids:
			var_ids += [p.id for p in product.product_variant_ids]
			# ####################################################################
		if product.is_pack:
			if product.wk_product_pack:
				for pp in product.wk_product_pack:
					var_ids += [pp.product_name.id]
			######################################################################
		variant_available = self.pool['product.product']._product_available(cr, uid, var_ids, context=context)
		for product in product_ids:
			qty_available = 0
			virtual_available = 0
			incoming_qty = 0
			outgoing_qty = 0
			for p in product.product_variant_ids:
				qty_available += variant_available[p.id]["qty_available"]
				virtual_available += variant_available[p.id]["virtual_available"]
				incoming_qty += variant_available[p.id]["incoming_qty"]
				outgoing_qty += variant_available[p.id]["outgoing_qty"]
			prod_available[product.id] = {
				"qty_available": qty_available,
				"virtual_available": virtual_available,
				"incoming_qty": incoming_qty,
				"outgoing_qty": outgoing_qty,
			}
            ##################################################################################
			if product.is_pack:
				if product.wk_product_pack:
					qty_avail = []
					vir_avail = []
					inco_qty = []
					outgo_qty = []
					for pp in product.wk_product_pack:
						qty_avail.append(variant_available[pp.product_name.id]["qty_available"]/pp.product_quantity)
						vir_avail.append(variant_available[pp.product_name.id]["virtual_available"]/pp.product_quantity)
						inco_qty.append(variant_available[pp.product_name.id]["incoming_qty"]/pp.product_quantity)
						outgo_qty.append(variant_available[pp.product_name.id]["outgoing_qty"]/pp.product_quantity)
					qty_available = min(qty_avail)
					virtual_available = min(vir_avail)
					incoming_qty = min(inco_qty)
					outgoing_qty = min(outgo_qty)
					prod_available[product.id] = {
						"qty_available": qty_available,
						"virtual_available": virtual_available,
						"incoming_qty": incoming_qty,
						"outgoing_qty": outgoing_qty,
						"qty_available_pack":qty_available,
						"virtual_available_pack":virtual_available,
						"incoming_qty_pack":outgoing_qty,
						"outgoing_qty_pack":outgoing_qty,
					}
			#########################################################################
		return prod_available

	def _search_product_quantity(self, cr, uid, obj, name, domain, context):
		prod = self.pool.get("product.product")
		product_variant_ids = prod.search(cr, uid, domain, context=context)
		return [('product_variant_ids', 'in', product_variant_ids)]
        
	_columns = {
		'qty_available': fields.function(_product_available, multi='qty_available', digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float', string='Quantity On Hand'),
        'virtual_available': fields.function(_product_available, multi='qty_available', digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float', string='Forecasted Quantity'),
        'incoming_qty': fields.function(_product_available, multi='qty_available', digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float', string='Incoming'),
        'outgoing_qty': fields.function(_product_available, multi='qty_available', digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float', string='Outgoing'),
        'qty_available_pack': fields.function(_product_available, multi='qty_available', digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float', string='Quantity On Hand'),
        'virtual_available_pack': fields.function(_product_available, multi='qty_available', digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float', string='Forecasted Quantity'),
        'incoming_qty_pack': fields.function(_product_available, multi='qty_available', digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float', string='Incoming'),
        'outgoing_qty_pack': fields.function(_product_available, multi='qty_available', digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float', string='Outgoing'),
	}


#------------------------ For displaying the stock of the pack in thhe variant created for the pack.------------------------------


# class product_product(osv.osv):
# 	_inherit = "product.product"


# 	def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
# 		context = context or {}
# 		field_names = field_names or []
		
# 		domain_products = [('product_id', 'in', ids)]
# 		domain_quant, domain_move_in, domain_move_out = [], [], []
# 		domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations(cr, uid, ids, context=context)
# 		domain_move_in += self._get_domain_dates(cr, uid, ids, context=context) + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
# 		domain_move_out += self._get_domain_dates(cr, uid, ids, context=context) + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
# 		domain_quant += domain_products

# 		if context.get('lot_id'):
# 			domain_quant.append(('lot_id', '=', context['lot_id']))
# 		if context.get('owner_id'):
# 			domain_quant.append(('owner_id', '=', context['owner_id']))
# 			owner_domain = ('restrict_partner_id', '=', context['owner_id'])
# 			domain_move_in.append(owner_domain)
# 			domain_move_out.append(owner_domain)
# 		if context.get('package_id'):
# 			domain_quant.append(('package_id', '=', context['package_id']))

# 		domain_move_in += domain_move_in_loc
# 		domain_move_out += domain_move_out_loc
# 		moves_in = self.pool.get('stock.move').read_group(cr, uid, domain_move_in, ['product_id', 'product_qty'], ['product_id'], context=context)
# 		moves_out = self.pool.get('stock.move').read_group(cr, uid, domain_move_out, ['product_id', 'product_qty'], ['product_id'], context=context)

# 		domain_quant += domain_quant_loc
# 		quants = self.pool.get('stock.quant').read_group(cr, uid, domain_quant, ['product_id', 'qty'], ['product_id'], context=context)
# 		quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))

# 		moves_in = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_in))
# 		moves_out = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_out))
# 		res = {}
# 		ctx = context.copy()
# 		ctx.update({'prefetch_fields': False})
# 		for product in self.browse(cr, uid, ids, context=ctx):

# 			id = product.id
# 			qty_available = float_round(quants.get(id, 0.0), precision_rounding=product.uom_id.rounding)
# 			incoming_qty = float_round(moves_in.get(id, 0.0), precision_rounding=product.uom_id.rounding)
# 			outgoing_qty = float_round(moves_out.get(id, 0.0), precision_rounding=product.uom_id.rounding)
# 			virtual_available = float_round(quants.get(id, 0.0) + moves_in.get(id, 0.0) - moves_out.get(id, 0.0), precision_rounding=product.uom_id.rounding)
			
# 			if product.is_pack:
# 				if product.wk_product_pack:
# 					qty_avail = []
# 					vir_avail = []
# 					inco_qty = []
# 					outgo_qty = []
# 					for pp in product.wk_product_pack:
# 						_id = pp.product_name.id
# 						qty_avail.append(float_round(quants.get(_id, 0.0), precision_rounding=pp.product_name.uom_id.rounding)/pp.product_quantity)
# 						vir_avail.append(float_round(quants.get(_id, 0.0) + moves_in.get(_id, 0.0) - moves_out.get(_id, 0.0), precision_rounding=pp.product_name.uom_id.rounding)/pp.product_quantity)
# 						inco_qty.append(float_round(moves_in.get(_id, 0.0), precision_rounding=pp.product_name.uom_id.rounding)/pp.product_quantity)
# 						outgo_qty.append(float_round(moves_out.get(_id, 0.0), precision_rounding=pp.product_name.uom_id.rounding)/pp.product_quantity)
					
# 					# _logger.info('--------%r .......%r.... %r-------%r', qty_avail, vir_avail, inco_qty,outgo_qty)

# 					qty_available = min(qty_avail)
# 					virtual_available = min(vir_avail)
# 					incoming_qty = min(inco_qty)
# 					outgoing_qty = min(outgo_qty)
# 			res[id] = {
# 				'qty_available': qty_available,
# 				'incoming_qty': incoming_qty,
# 				'outgoing_qty': outgoing_qty,
# 				'virtual_available': virtual_available,
# 			}
			
# 		return res


# 	def _search_product_quantity(self, cr, uid, obj, name, domain, context):
# 		res = []
# 		for field, operator, value in domain:
# 			#to prevent sql injections
# 			assert field in ('qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'), 'Invalid domain left operand'
# 			assert operator in ('<', '>', '=', '!=', '<=', '>='), 'Invalid domain operator'
# 			assert isinstance(value, (float, int)), 'Invalid domain right operand'

# 			if operator == '=':
# 				operator = '=='

# 			ids = []
# 			if name == 'qty_available' and (value != 0.0 or operator not in  ('==', '>=', '<=')):
# 				res.append(('id', 'in', self._search_qty_available(cr, uid, operator, value, context)))
# 			else:
# 				product_ids = self.search(cr, uid, [], context=context)
# 				if product_ids:
# 				#TODO: Still optimization possible when searching virtual quantities
# 					for element in self.browse(cr, uid, product_ids, context=context):
# 						if eval(str(element[field]) + operator + str(value)):
# 							ids.append(element.id)
# 					res.append(('id', 'in', ids))
# 			return res


# 	_columns = {
# 		'qty_available': fields.function(_product_available, multi='qty_available',
#             type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
#             string='Quantity On Hand',
#             fnct_search=_search_product_quantity,
#             help="Current quantity of products.\n"
#                  "In a context with a single Stock Location, this includes "
#                  "goods stored at this Location, or any of its children.\n"
#                  "In a context with a single Warehouse, this includes "
#                  "goods stored in the Stock Location of this Warehouse, or any "
#                  "of its children.\n"
#                  "stored in the Stock Location of the Warehouse of this Shop, "
#                  "or any of its children.\n"
#                  "Otherwise, this includes goods stored in any Stock Location "
#                  "with 'internal' type."),
#         'virtual_available': fields.function(_product_available, multi='qty_available',
#             type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
#             string='Forecast Quantity',
#             fnct_search=_search_product_quantity,
#             help="Forecast quantity (computed as Quantity On Hand "
#                  "- Outgoing + Incoming)\n"
#                  "In a context with a single Stock Location, this includes "
#                  "goods stored in this location, or any of its children.\n"
#                  "In a context with a single Warehouse, this includes "
#                  "goods stored in the Stock Location of this Warehouse, or any "
#                  "of its children.\n"
#                  "Otherwise, this includes goods stored in any Stock Location "
#                  "with 'internal' type."),
#         'incoming_qty': fields.function(_product_available, multi='qty_available',
#             type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
#             string='Incoming',
#             fnct_search=_search_product_quantity,
#             help="Quantity of products that are planned to arrive.\n"
#                  "In a context with a single Stock Location, this includes "
#                  "goods arriving to this Location, or any of its children.\n"
#                  "In a context with a single Warehouse, this includes "
#                  "goods arriving to the Stock Location of this Warehouse, or "
#                  "any of its children.\n"
#                  "Otherwise, this includes goods arriving to any Stock "
#                  "Location with 'internal' type."),
#         'outgoing_qty': fields.function(_product_available, multi='qty_available',
#             type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
#             string='Outgoing',
#             fnct_search=_search_product_quantity,
#             help="Quantity of products that are planned to leave.\n"
#                  "In a context with a single Stock Location, this includes "
#                  "goods leaving this Location, or any of its children.\n"
#                  "In a context with a single Warehouse, this includes "
#                  "goods leaving the Stock Location of this Warehouse, or "
#                  "any of its children.\n"
#                  "Otherwise, this includes goods leaving any Stock "
#                  "Location with 'internal' type."),
# 	}