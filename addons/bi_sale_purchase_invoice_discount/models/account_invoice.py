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
from openerp.tools import float_is_zero
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import time

class account_account(models.Model):
    _inherit = 'account.account'
    
    discount_account = fields.Boolean('Discount Account')
    
    
class account_invoice(models.Model):
    _inherit = 'account.invoice'   
    
    @api.depends('discount_value')
    @api.multi
    def _compute_amount_after_discount(self):
        res = discount = 0.0
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        for self_obj in self:
            if self.discount_type_id.id == discount_type_fixed:
                res = self_obj.discount_value
            elif self.discount_type_id.id == discount_type_percent:
                res = self_obj.amount_untaxed * (self_obj.discount_value/ 100)
            else:
                res = discount
        return res
            
            
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id','discount_value','discount_type_id')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        res = self._compute_amount_after_discount()
        self.discount_amt = res
        self.amount_total = self.amount_untaxed - res + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            amount_total_company_signed = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
    
    @api.model
    def discount_line_move_line_get(self):
        res = []
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        for i in self:
            if self.discount_type_id.id == discount_type_fixed:
                value = i.discount_value
            elif self.discount_type_id.id == discount_type_percent:
                value = i.amount_untaxed * (i.discount_value/ 100)
            else:
                value = 0.0 
            res.append( {
                    'name': i.discount_type_id.name,
                    'price_unit': value,
                    'quantity': 1,
                    'price': -value,
                    'account_id': i.discount_account.id,
                } )
            res.append({
                    'name': '/',
                    'price_unit':value,
                    'quantity': 1,
                    'price': value,
                    'account_id': i.account_id.id,
                })
        return res
    

#            
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue
            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()
            if self.discount_value:
                iml += inv.discount_line_move_line_get()
#                iml+= inv.partner_line_move_line_get()
            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)
            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=inv.currency_id.id).compute(total, date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id,
                    })
                
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id,
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)
            
            date = inv.date or date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['dont_create_taxes'] = True
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True
        
    discount_type_id = fields.Many2one('discount.type', 'Discount Type' , readonly = True)
    discount_value = fields.Float('Discount Value',readonly = True)
    discount_account = fields.Many2one('account.account', 'Discount Account', readonly = True)
    amount_after_discount = fields.Monetary('Amount After Discount' , store=True, readonly=True)
    
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    @api.model
    def create(self, vals, apply_taxes=True):
        """ :param apply_taxes: set to False if you don't want vals['tax_ids'] to result in the creation of move lines for taxes and eventual
                adjustment of the line amount (in case of a tax included in price). This is useful for use cases where you don't want to
                apply taxes in the default fashion (eg. taxes). You can also pass 'dont_create_taxes' in context.

            :context's key `check_move_validity`: check data consistency after move line creation. Eg. set to false to disable verification that the move
                debit-credit == 0 while creating the move lines composing the move.

        """
        AccountObj = self.env['account.account']
        MoveObj = self.env['account.move']
        context = dict(self._context or {})
        amount = vals.get('debit', 0.0) - vals.get('credit', 0.0)
        if not vals.get('partner_id') and context.get('partner_id'):
            vals['partner_id'] = context.get('partner_id')
        if vals.get('move_id', False):
            move = MoveObj.browse(vals['move_id'])
            if move.date and not vals.get('date'):
                vals['date'] = move.date
        if ('account_id' in vals) and AccountObj.browse(vals['account_id']).deprecated:
            raise UserError(_('You cannot use deprecated account.'))
        if 'journal_id' in vals and vals['journal_id']:
            context['journal_id'] = vals['journal_id']
        if 'date' in vals and vals['date']:
            context['date'] = vals['date']
        if ('journal_id' not in context) and ('move_id' in vals) and vals['move_id']:
            m = MoveObj.browse(vals['move_id'])
            context['journal_id'] = m.journal_id.id
            context['date'] = m.date
        #we need to treat the case where a value is given in the context for period_id as a string
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            context['journal_id'] = context.get('search_default_journal_id')
        if 'date' not in context:
            context['date'] = fields.Date.context_today(self)
        move_id = vals.get('move_id', False)
        journal = self.env['account.journal'].browse(context['journal_id'])
        vals['journal_id'] = vals.get('journal_id') or context.get('journal_id')
        vals['date'] = vals.get('date') or context.get('date')
        vals['date_maturity'] = vals.get('date_maturity') if vals.get('date_maturity') else vals['date']
        if not move_id:
            if not vals.get('move_id', False):
                if journal.sequence_id:
                    #name = self.pool.get('ir.sequence').next_by_id(cr, uid, journal.sequence_id.id)
                    v = {
                        'date': vals.get('date', time.strftime('%Y-%m-%d')),
                        'journal_id': context['journal_id']
                    }
                    if vals.get('ref', ''):
                        v.update({'ref': vals['ref']})
                    move_id = MoveObj.with_context(context).create(v)
                    vals['move_id'] = move_id.id
                else:
                    raise UserError(_('Cannot create an automatic sequence for this piece.\nPut a sequence in the journal definition for automatic numbering or create a sequence manually for this piece.'))
        ok = not (journal.type_control_ids or journal.account_control_ids)
        if ('account_id' in vals):
            account = AccountObj.browse(vals['account_id'])
            if journal.type_control_ids:
                type = account.user_type_id
                for t in journal.type_control_ids:
                    if type == t:
                        ok = True
                        break
            if journal.account_control_ids and not ok:
                for a in journal.account_control_ids:
                    if a.id == vals['account_id']:
                        ok = True
                        break
            # Automatically convert in the account's secondary currency if there is one and
            # the provided values were not already multi-currency
            if account.currency_id and 'amount_currency' not in vals and account.currency_id.id != account.company_id.currency_id.id:
                vals['currency_id'] = account.currency_id.id
                ctx = {}
                if 'date' in vals:
                    ctx['date'] = vals['date']
                vals['amount_currency'] = account.company_id.currency_id.with_context(ctx).compute(amount, account.currency_id)
        if not ok:
            raise UserError(_('You cannot use this general account in this journal, check the tab \'Entry Controls\' on the related journal.'))

        # Create tax lines
        tax_lines_vals = []
        if apply_taxes and not context.get('dont_create_taxes') and vals.get('tax_ids'):
            # Get ids from triplets : https://www.odoo.com/documentation/master/reference/orm.html#openerp.models.Model.write
            tax_ids = [tax['id'] for tax in self.resolve_2many_commands('tax_ids', vals['tax_ids']) if tax.get('id')]
            # Since create() receives ids instead of recordset, let's just use the old-api bridge
            taxes = self.env['account.tax'].browse(tax_ids)
            currency = self.env['res.currency'].browse(vals.get('currency_id'))
            res = taxes.compute_all(amount,
                currency, 1, vals.get('product_id'), vals.get('partner_id'))
            # Adjust line amount if any tax is price_include
            if abs(res['total_excluded']) < abs(amount):
                if vals['debit'] != 0.0: vals['debit'] = res['total_excluded']
                if vals['credit'] != 0.0: vals['credit'] = -res['total_excluded']
                if vals.get('amount_currency'):
                    vals['amount_currency'] = self.env['res.currency'].browse(vals['currency_id']).round(vals['amount_currency'] * (amount / res['total_excluded']))
            # Create tax lines
            for tax_vals in res['taxes']:
                if tax_vals['amount']:
                    account_id = (amount > 0 and tax_vals['account_id'] or tax_vals['refund_account_id'])
                    if not account_id: account_id = vals['account_id']
                    tax_lines_vals.append({
                        'account_id': account_id,
                        'name': vals['name'] + ' ' + tax_vals['name'],
                        'tax_line_id': tax_vals['id'],
                        'move_id': vals['move_id'],
                        'date': vals['date'],
                        'partner_id': vals.get('partner_id'),
                        'ref': vals.get('ref'),
                        'statement_id': vals.get('statement_id'),
                        'debit': tax_vals['amount'] > 0 and tax_vals['amount'] or 0.0,
                        'credit': tax_vals['amount'] < 0 and -tax_vals['amount'] or 0.0,
                    })

        new_line = super(AccountMoveLine, self).create(vals)
        for tax_line_vals in tax_lines_vals:
            # TODO: remove .with_context(context) once this context nonsense is solved
            self.with_context(context).create(tax_line_vals)
        if self._context.get('check_move_validity', True):
            move = MoveObj.browse(vals['move_id'])
            move.with_context(context)._post_validate()
        return new_line
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
