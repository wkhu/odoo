# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Dynamic Product Small Label",
    'version': '1.1',
    'category': 'Product',
    'description': """
        User can create custom label template by frontend and can print the dynamic product label report.
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'summary': 'Create custom label template and print dynamic product label report.',
    'depends': ['base', 'sale', 'purchase', 'stock', 'account', 'mrp'],
    'price': 149, 
    'currency': 'EUR',
    'data': [
         'views/prod_small_lbl_rpt.xml',
         'views/wizard_product_small_label_report.xml',
         'security/ir.model.access.csv',
         'dynamic_product_small_label_report.xml',
         'data/design_data.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
