# -*- coding: utf-8 -*-
##############################################################################
#
#    Sales , Purchase and Account Invoice Discount Management
#    Copyright (C) 2015 BrowseInfo(<http://www.browseinfo.in>).
#    $autor:
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import api, fields, models, _
from openerp.exceptions import UserError

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    @api.model
    def create(self, vals):
        res = super(purchase_order, self).create(vals)
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        if vals.get('discount_value'):
            discount_type_obj = self.env['discount.type']
            if vals.get('discount_type_id') == discount_type_percent:
                brw_type = discount_type_obj.browse(discount_type_percent).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value') > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s %. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type') % \
                        (brw_type))
            elif vals.get('discount_type_id') == discount_type_fixed:
                brw_type = discount_type_obj.browse(discount_type_fixed).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value') > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type' ) % \
                        (brw_type ,brw_type ))
        return res
    
    @api.onchange('apply_discount')
    def onchange_apply_discount(self):
        if self.apply_discount:
            account_search = self.env['account.account'].search([('discount_account', '=', True),('user_type_id.name','=','Income')])
            if account_search:
                self.discount_account = account_search[0].id
    
    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_discount_account': self.discount_account.id , 'default_purchase_id': self.id, 'default_amount_after_discount' : self.amount_after_discount, 'default_discount_type_id' : self.discount_type_id.id , 'default_discount_value' : self.discount_value , 'default_amount_untaxed' : self.amount_untaxed}
        result['domain'] = "[('purchase_id', '=', %s)]" % self.id
        invoice_ids = sum([order.invoice_ids.ids for order in self], [])
        # choose the view_mode accordingly
        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, invoice_ids)) + "])]"
        elif len(invoice_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = invoice_ids and invoice_ids[0] or False
        return result        
    
    @api.depends('order_line.price_total','amount_after_discount')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if order.apply_discount == True:
                order.update({
                    'amount_untaxed': order.currency_id.round(amount_untaxed),
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_total': order.amount_after_discount + amount_tax ,
                }) 
            else:
                order.update({
                    'amount_untaxed': order.currency_id.round(amount_untaxed),
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_total': amount_untaxed + amount_tax ,
                })  
                
    @api.depends('discount_value')
    def _compute_amount_after_discount(self):
        discount = 0.0
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        for self_obj in self:
            if self_obj.discount_type_id.id == discount_type_fixed:
                discount = self_obj.amount_untaxed - self_obj.discount_value
                self_obj.amount_after_discount = discount
            elif self.discount_type_id.id == discount_type_percent:
                discount_percent = self_obj.amount_untaxed * ((self_obj.discount_value or 0.0) / 100.0)
                discount = self_obj.amount_untaxed - discount_percent
                self_obj.amount_after_discount = discount
            else:
                self_obj.amount_after_discount = discount
    
    apply_discount = fields.Boolean('Apply Discount')
    discount_type_id = fields.Many2one('discount.type', 'Discount Type')
    discount_value = fields.Float('Purchase Discount')
    discount_account = fields.Many2one('account.account', 'Discount Account')
    amount_after_discount = fields.Monetary('Amount After Discount' , store=True, readonly=True, compute='_compute_amount_after_discount')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
