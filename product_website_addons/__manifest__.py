# -*- coding: utf-8 -*-
{
    'name': 'Website Product Enhancements',
    'version': '1.0',
    'summary': 'Enhance product display and editing features on the website',
    'description': '''
        Améliore l’affichage et l’édition des produits sur le site web Odoo.
        Permet l’édition des produits en front-end, l’affichage enrichi des prix,
        et l'intégration avec les modèles de commandes pour une meilleure expérience client.
    ''',
    'author': "OBG",
    'license': 'LGPL-3',
    'website': "https://www.obg.tn/",
    'images': ['module_icon.png',
               ],

    'category': 'Website',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'website', 'website_sale', 'website_sale_comparison', 'web', 'account'],
    # 'assets': {
    #     'web._assets_primary_variables': [
    #         'product_website_addons/static/src/js/product_sku_update.js',
    #     ],
    # },

    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        # 'views/assets.xml',
        'views/edit_product_view_website.xml',
        'views/product_price_inherit.xml',
        'views/edit_sale_order_template.xml',
        'views/product_product.xml',
        'report/devis_template.xml',
        'report/delivery_template.xml',
        'report/facture_template.xml',
        'views/sale_order.xml',
    ],

    'installable': True,
    'application': True,
}
