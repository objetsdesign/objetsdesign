{
        "name": "Interco Status & Sync (OD ↔ BSI ↔ VRI)",
        'version': '1.0',
        'summary': 'Ajout de statuts métier personnalisés aux commandes d’achat',
        'author': 'VON ROSS',
        'depends': ['purchase','mrp','sale'],
        'data': [
            'security/ir.model.access.csv',
            'data/group.xml',
            'views/purchase_order_views_inherit.xml',
            'views/res_company.xml',
            # 'views/sale_order.xml',
            'views/mrp_bom.xml',
            'views/res_partner.xml',
        ],
        'assets': {
            'web.assets_backend': [
                'sale_and_purchase_process/static/src/scss/style.scss',

            ],
    },

    'installable': True,
    }
