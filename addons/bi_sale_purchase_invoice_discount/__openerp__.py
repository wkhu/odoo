# -*- coding: utf-8 -*-
##############################################################################
#
#    Sales , Purchase nd Invoice Discount Management
#    Copyright (C) 2015 BrowseInfo(<http://www.browseinfo.in>).
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
{
    'name': 'Global Discount on Sales,Purchase & Invoice with Tax calculation',
    'version': '1.0',
    'category': 'Sales , Purchase & Invoice',
    'sequence': 14,
    'summary': 'Discount on Sales,Purchase & Invoice with Tax calculation',
    'price': '55',
    'currency': "EUR",
    'description': """
Manage sales orders and Invoice  Discount
=========================================
Manages the Discount in Sale order , Purchase Order and in whole Sale order/Purchase order basis on Fix
and Percentage wise as well as calculate tax before discount and after
discount and same for the Invoice.
""",
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'images': [],
    'depends': ['sale', 'account', 'purchase','account_accountant'],
    'data': [
            'security/ir.model.access.csv',
            'views/discount_type_view.xml',
            'views/sale_purchase_account_view.xml',
            'report/inherit_sale_report.xml',
            'report/inherit_purchase_report.xml',
            'report/inherit_account_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
