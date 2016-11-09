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


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    picking_id = fields.Many2one('stock.picking', string="Picking", store=True, copy=False)


    @api.multi
    def create_shipment(self):
        if self.picking_id:
            raise Warning(_("Picking Already Created."))
        obj_picking = self.env['stock.picking']
        obj_stock_move = self.env['stock.move']
        obj_picking_type = self.env['stock.picking.type']
        all_fields = obj_picking.fields_get([])
        default_get_receipt = obj_picking.default_get(all_fields.keys())
        default_get_receipt['partner_id'] = self.partner_id.id
        picking_type = obj_picking_type.search([('code', '=', 'incoming'),('warehouse_id.company_id', '=', self.company_id.id)])
        default_get_receipt['picking_type_id'] = picking_type.id
        picking = obj_picking.new(default_get_receipt)
        change_partner = picking.onchange_picking_type(picking_type_id=picking_type.id,partner_id=self.partner_id.id)
        default_get_receipt.update(change_partner['value'])
        prod_list = []
        for each in self.invoice_line_ids:
            if each.product_id:
                prod_vals = obj_stock_move.onchange_product_id(prod_id=each.product_id.id,
                                                       loc_id=default_get_receipt['location_id'],
                                                       loc_dest_id=default_get_receipt['location_id'],
                                                       partner_id=self.partner_id.id)
                prod_vals.get('value').update({'product_uom_qty':each.quantity})
                prod_vals['value']['product_id'] = each.product_id.id
                prod_list.append((0, 0, prod_vals['value']))
            else:
                raise Warning(_("Please insert product in invoice line."))
        default_get_receipt.update({'origin':self.number,'state':'draft','move_lines':prod_list})
        pick_id = obj_picking.create(default_get_receipt)
        self.write({'picking_id': pick_id.id})
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'res_id': pick_id.id or False,
                'type': 'ir.actions.act_window',
                }