
# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################

{
    'name': 'POS Customer screen',
    'version': '1.0',
    'category': 'Point of Sale',
    'website': 'http://www.acespritech.com',
    'price': 0,
    'currency': 'EUR',
    'summary': '',
    'description': "",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "www.acespritech.com",
    'depends': ['point_of_sale'],
#     'images': ['static/description/main_screenshot.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_mirror_image.xml',
        'views/pos_mirror_image_template.xml',
    ],
    'qweb': ['static/src/xml/pos.xml',],
    'installable': True,
    'auto_install': False
}
