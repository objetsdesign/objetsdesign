{
        "name": "Rectification Fiche Client",
        'version': '1.0',
        'summary': 'Modification au niveau de fiche client suivant le besoin',
        'author': 'VON ROSS',
        'depends': ['sale','base','web'],
        'data': [
            'security/ir.model.access.csv',
            'data/filtre.xml',
            'views/res_partner.xml',
        ],
        'assets': {
            'web.assets_backend': [
                'fiche_client_objets_design/static/src/scss/style.scss',

            ],
    },
        'installable': True,
    }
