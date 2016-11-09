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


class product_brand(models.Model):
    _name = 'product.brand'

    code = fields.Char(string="Code")
    name = fields.Char(string="Name")
    logo = fields.Binary(string="Logo")

    _sql_constraints = [
        ('brand_code', 'unique(code)', 'Brand Code should be unique!'),
    ]


class product_template(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        res = super(product_template, self).create(vals)
        external_reference = self.env['ir.sequence'].get('external.reference')
        if res:
            res.write({'external_reference':external_reference})
        return res

    external_reference = fields.Char(string="External Reference")
    brand_id = fields.Many2one('product.brand', string="Brand Ref.")
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
