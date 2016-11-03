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


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"  
      
    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']
        
        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id
        if not account_id:
            prop = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            prop_id = prop and prop.id or False
            account_id = order.fiscal_position_id.map_account(prop_id)
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') % \
                    (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
        
        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'discount_type_id': self.discount_type_id.id,
            'discount_value': self.discount_value,
            'amount_after_discount': self.amount_after_discount,
            'discount_account':self.discount_account.id,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, [x.id for x in self.product_id.taxes_id])],
                'account_analytic_id': order.project_id.id or False,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
        })
        invoice.compute_taxes()
        return invoice
    
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def create(self, vals):
        res = super(sale_order, self).create(vals)
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
            account_search = self.env['account.account'].search([('discount_account', '=', True),('user_type_id.name','=','Expenses')])
            if account_search:
                self.discount_account = account_search[0].id
    
    @api.depends('order_line.price_total','amount_after_discount' )
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
     
    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserWarning(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'reference': self.client_order_ref or self.name,
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'journal_id': journal_id,
            'discount_type_id': self.discount_type_id.id,
            'discount_value': self.discount_value,
            'amount_after_discount': self.amount_after_discount,
            'discount_account':self.discount_account.id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        return invoice_vals
       
    
    apply_discount = fields.Boolean('Apply Discount')
    discount_type_id = fields.Many2one('discount.type', 'Discount Type')
    discount_value = fields.Float('Sale Discount')
    discount_account = fields.Many2one('account.account', 'Discount Account')
    amount_after_discount = fields.Monetary('Amount After Discount' , store=True, readonly=True , compute = '_compute_amount_after_discount',digits_compute=dp.get_precision('Account'))
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
