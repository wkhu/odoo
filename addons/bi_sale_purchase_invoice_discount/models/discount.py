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

from openerp.tools.translate import _
from openerp import api, fields, models, _
from openerp.exceptions import UserError

class discount(models.Model):
    _name = 'discount.type'
    
    name = fields.Char('Discount Name')
    discount_value = fields.Float('Discount Value')
    