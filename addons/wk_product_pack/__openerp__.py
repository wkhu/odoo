# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
{
    "name": "Product Pack",
    "category": 'Sales Management',
    "summary": """
       Combine two or more products together in order to create a bundle product.""",
    "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: wk_product_pack/static/src/img/icon-features.png
.. |icon_support| image:: wk_product_pack/static/src/img/icon-support.png
.. |icon_help| image:: wk_product_pack/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '2.1',
    "depends": ['sale','product','stock','sale_stock'],
    "data": [
        'wizard/product_pack_wizard.xml',
        'views/wk_product_pack.xml',
        'views/inherited_stock_view.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 69,
    "currency": 'EUR',
    "images":['static/description/Banner.png']
}