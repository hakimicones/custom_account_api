# -*- coding: utf-8 -*-
{
    'name': 'Custom Account API',
    'version': '16.0.1.0.0',
    'category': 'Custom',
    'summary': 'Gestion des comptes utilisateurs (Producteur / Waste-Picker / Client) avec API REST',
    'description': """
        Module de gestion des comptes utilisateurs pour la plateforme de gestion de déchets.
        - Modèle utilisateur avec rôles (Producteur, Waste-Picker)
        - Permissions et record rules par rôle
        - API REST pour inscription, authentification et gestion des profils
    """,
    'author': 'NOUAS A/Hakim',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/utilisateur_views.xml',
        'views/utilisateur_menus.xml',
        'data/data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
