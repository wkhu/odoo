# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-TODAY Acespritech Solutions Pvt Ltd
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
from openerp import fields, models, api, _
from openerp.exceptions import Warning
import datetime
from datetime import timedelta

class sale_order(models.Model):
    _inherit = 'sale.order'


    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
       """
       Update the following fields when the partner is changed:
       - Pricelist
       - Payment term
       - Invoice address
       - Delivery address
       """
       if not self.partner_id:
           self.update({
               'partner_invoice_id': False,
               'partner_shipping_id': False,
               'fiscal_position_id': False,
           })
           return

       addr = self.partner_id.address_get(['delivery', 'invoice'])
       values = {
           'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
           'partner_invoice_id': addr['invoice'],
           'partner_shipping_id': addr['delivery'],
       }
       if self.env.user.company_id.sale_note:
           values['note'] = self.with_context(lang=self.partner_id.lang).env.user.company_id.sale_note

       if self.partner_id.user_id:
           values['user_id'] = self.partner_id.user_id.id
       if self.partner_id.team_id:
           values['team_id'] = self.partner_id.team_id.id
       self.update(values)
        
            
    @api.model
    def default_get(self, fields_list):
       res = super(sale_order, self).default_get(fields_list)
       incoterm_id = self.env['stock.incoterms'].search([('code', '=', 'EXW')])
       if incoterm_id:
           res.update({'incoterm':incoterm_id.id})
       payment_id = self.env['ir.model.data'].get_object_reference('account', 'account_payment_term_immediate')[1]
       if payment_id:
           res.update({'payment_term_id':payment_id})
       validity_date = datetime.date.today() + datetime.timedelta(days=30)
       res.update({'validity_date':validity_date.strftime('%Y-%m-%d')})
       return res

    @api.multi
    @api.depends('order_line.product_id')
    def _get_lead_time(self):
        for each_order in self:
            highest_time = 0
            for each_order_line in each_order.order_line:
                if each_order_line.product_id.sale_delay > highest_time:
                    highest_time = each_order_line.product_id.sale_delay
            each_order.lead_time = highest_time
        return True

    validity_date = fields.Date(string='Validity Date', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    order_created = fields.Boolean(string="Created")
    lead_time = fields.Integer(string="Lead Time", compute='_get_lead_time', store=True)
#     custom_tax_id = fields.Many2one('account.tax', string="Tax", domain=['|', ('active', '=', False), ('active', '=', True)])

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            if self._context.get('from_action_confirm'):
                 vals['name'] = 'New'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.quotation') or '/'

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(sale_order, self).create(vals)
        return result

    @api.multi
    def action_confirm(self):
        if not self.order_created:
            order_id = self.with_context({'from_action_confirm':True}).copy()
            self.write({'order_created':True})
            order_id.write({'name': self.name.replace('Q', 'O') or False,
                            'order_created':True})
            res = super(sale_order, order_id).action_confirm()
            if order_id:
                view_id = self.env['ir.model.data'].get_object_reference('sale', 'view_order_form')[1]
                return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': [view_id],
                    'res_id': order_id.id or False,
                    'type': 'ir.actions.act_window',
                }
        else:
            raise Warning(_('Order is already Confirmed'))

#     @api.multi
#     def button_dummy(self):
#         for order in self:
#             amount_untaxed = amount_tax = 0.0
#             for line in order.order_line:
#                 amount_untaxed += line.price_subtotal
#             order.update({
#                 'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
#                 'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
#                 'amount_total': amount_untaxed + amount_tax,
#             })
# #             tax = order.custom_tax_id.compute_all(order.amount_untaxed)
# # #             amount_tax = tax['total_included'] - tax['total_excluded']
# #             order.update({
# #                 'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
# #                 'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
# #                 'amount_total': amount_untaxed + amount_tax,
# #             })
#         return True

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            vals['product_uom'] = self.product_id.uom_id

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name


        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = product.price
        self.update(vals)
        return {'domain': domain}

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date_order=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = product.price

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
