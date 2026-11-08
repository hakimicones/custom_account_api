# -*- coding: utf-8 -*-
"""Tests REST API du module custom_account_api."""
import json
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestUtilisateurAPI(HttpCase):
    """Tests de l'API REST utilisateur."""

    def _post_json(self, path, data):
        response = self.url_open(
            path,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
        )
        return response.json()

    def test_01_register_producteur(self):
        """Tester l'inscription d'un producteur via l'API REST."""
        # Données d'inscription
        data = {
            'nom': 'Dupont',
            'prenom': 'Jean',
            'email': 'jean.dupont@test.com',
            'mot_de_passe': 'MotDePasse123',
            'role': 'producteur',
        }

        # Appel de l'endpoint d'inscription
        result = self._post_json('/api/utilisateur/register', data)

        # Vérification
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('data')['role'], 'producteur')
        self.assertEqual(result.get('data')['email'], 'jean.dupont@test.com')

    def test_02_login_producteur(self):
        """Tester la connexion d'un producteur."""
        # D'abord on inscrit
        self.test_01_register_producteur()

        # Then on se connecte
        data = {
            'email': 'jean.dupont@test.com',
            'mot_de_passe': 'MotDePasse123',
        }

        result = self._post_json('/api/utilisateur/login', data)

        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('data')['email'], 'jean.dupont@test.com')

    def test_03_list_users_producteur(self):
        """Tester la liste des utilisateurs (producteur uniquement)."""
        # On inscrit un second producteur
        data = {
            'nom': 'Martin',
            'prenom': 'Marie',
            'email': 'marie.martin@test.com',
            'mot_de_passe': 'MotDePasse123',
            'role': 'producteur',
        }
        self._post_json('/api/utilisateur/register', data)

        # Liste des producteurs
        result = self._post_json('/api/utilisateur/list', {'role': 'producteur'})

        self.assertTrue(result.get('success'))
        self.assertGreaterEqual(result.get('count', 0), 2)

    def test_04_get_profile_own(self):
        """Tester la récupération de son propre profil."""
        registration = self._post_json('/api/utilisateur/register', {
            'nom': 'Dupont',
            'prenom': 'Jean',
            'email': 'jean.profile@test.com',
            'mot_de_passe': 'MotDePasse123',
            'role': 'producteur',
        })
        utilisateur_id = registration['data']['id']

        response = self.url_open('/api/utilisateur/%s' % utilisateur_id)
        result = response.json()

        self.assertTrue(result.get('success'))
        self.assertEqual(result['data']['id'], utilisateur_id)

    def test_05_waste_picker_can_create_account(self):
        """Tester que waste-picker peut créer son compte (nouvelle règle)."""
        data = {
            'nom': 'Ramasy',
            'prenom': 'Paul',
            'email': 'paul.ramasy@test.com',
            'mot_de_passe': 'MotDePasse123',
            'role': 'waste_picker',
        }

        result = self._post_json('/api/utilisateur/register', data)

        # La règle actuelle permet waste-picker de créer son compte
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('data')['role'], 'waste_picker')