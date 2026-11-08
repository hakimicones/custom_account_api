# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash


class Utilisateur(models.Model):
    _name = 'custom.utilisateur'
    _description = 'Utilisateur (Producteur / Waste-Picker)'
    _rec_name = 'nom_complet'

    # --- Champs principaux ---
    client_id = fields.Char(
        string='Identifiant Client',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('custom.utilisateur') or '/',
    )
    nom = fields.Char(string='Nom', required=True)
    prenom = fields.Char(string='Prénom', required=True)
    nom_complet = fields.Char(
        string='Nom Complet',
        compute='_compute_nom_complet',
        store=True,
    )
    email = fields.Char(string='Email', required=True)
    mot_de_passe = fields.Char(string='Mot de passe (hashé)')
    role = fields.Selection(
        selection=[
            ('producteur', 'Producteur'),
            ('waste_picker', 'Waste-Picker'),
        ],
        string='Rôle',
        required=True,
        default='producteur',
    )
    active = fields.Boolean(string='Actif', default=True)

    # --- Relations ---
    app_mobile_id = fields.Many2one(
        comodel_name='custom.utilisateur',
        string='Lié à App Mobile',
        help="Lien vers le compte utilisateur de l'app mobile.",
    )
    waste_picker_id = fields.Many2one(
        comodel_name='custom.utilisateur',
        string='Waste-Picker associé',
        domain="[('role', '=', 'waste_picker')]",
        help="Waste-Picker associé à ce producteur.",
    )

    # --- Contraintes SQL ---
    _sql_constraints = [
        ('unique_client_id', 'UNIQUE(client_id)', 'L\'identifiant client doit être unique.'),
        ('unique_email', 'UNIQUE(email)', 'Cet email est déjà utilisé.'),
    ]

    # --- Champs calculés ---
    @api.depends('nom', 'prenom')
    def _compute_nom_complet(self):
        for rec in self:
            rec.nom_complet = f"{rec.prenom or ''} {rec.nom or ''}".strip()

    # --- Validations ---
    @api.constrains('email')
    def _check_email(self):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for rec in self:
            if rec.email and not re.match(email_regex, rec.email):
                raise ValidationError("L'adresse email '%s' n'est pas valide." % rec.email)

    # --- Méthodes de mot de passe ---
    def set_mot_de_passe(self, mot_de_passe_clair):
        """Hash et enregistre le mot de passe."""
        self.ensure_one()
        self.mot_de_passe = generate_password_hash(mot_de_passe_clair)

    def verifier_mot_de_passe(self, mot_de_passe_clair):
        """Vérifie un mot de passe en clair contre le hash stocké."""
        self.ensure_one()
        if not self.mot_de_passe:
            return False
        return check_password_hash(self.mot_de_passe, mot_de_passe_clair)
