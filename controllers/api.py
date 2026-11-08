import json

from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from odoo import http
from odoo.http import request


def _json_response(payload, status=200):
    response = request.make_response(
        json.dumps(payload),
        headers=[('Content-Type', 'application/json; charset=utf-8')],
    )
    response.status_code = status
    return response


def _read_json_body():
    if not request.httprequest.is_json:
        return None, _json_response(
            {'success': False, 'error': 'Le Content-Type doit être application/json.'},
            415,
        )

    try:
        body = request.httprequest.get_json()
    except (BadRequest, UnsupportedMediaType):
        return None, _json_response(
            {'success': False, 'error': 'Le corps JSON est invalide.'},
            400,
        )

    if not isinstance(body, dict):
        return None, _json_response(
            {'success': False, 'error': 'Le corps JSON doit être un objet.'},
            400,
        )

    return body, None


class UtilisateurAPI(http.Controller):
    """API REST pour la gestion des utilisateurs."""

    # --- Inscription ---
    @http.route('/api/utilisateur/register', type='http', auth='public', methods=['POST'], csrf=False)
    def register(self, **kwargs):
        """Créer un nouveau compte utilisateur."""
        body, error = _read_json_body()
        if error:
            return error

        required_fields = ['nom', 'prenom', 'email', 'mot_de_passe', 'role']
        missing = [f for f in required_fields if not body.get(f)]
        if missing:
            return _json_response({
                'success': False,
                'error': 'Champs manquants: %s' % ', '.join(missing),
            })

        # Vérifier si l'email existe déjà
        existing = request.env['custom.utilisateur'].sudo().search([('email', '=', body['email'])], limit=1)
        if existing:
            return _json_response({
                'success': False,
                'error': 'Un compte avec cet email existe déjà.',
            })

        # Créer l'utilisateur
        utilisateur = request.env['custom.utilisateur'].sudo().create({
            'nom': body['nom'],
            'prenom': body['prenom'],
            'email': body['email'],
            'role': body['role'],
        })
        utilisateur.set_mot_de_passe(body['mot_de_passe'])

        return _json_response({
            'success': True,
            'data': {
                'id': utilisateur.id,
                'client_id': utilisateur.client_id,
                'nom_complet': utilisateur.nom_complet,
                'email': utilisateur.email,
                'role': utilisateur.role,
            },
        })

    # --- Authentification ---
    @http.route('/api/utilisateur/login', type='http', auth='public', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        """Authentifier un utilisateur par email et mot de passe."""
        body, error = _read_json_body()
        if error:
            return error

        email = body.get('email')
        mot_de_passe = body.get('mot_de_passe')

        if not email or not mot_de_passe:
            return _json_response({
                'success': False,
                'error': 'Email et mot de passe requis.',
            })

        utilisateur = request.env['custom.utilisateur'].sudo().search([('email', '=', email)], limit=1)
        if not utilisateur or not utilisateur.verifier_mot_de_passe(mot_de_passe):
            return _json_response({
                'success': False,
                'error': 'Email ou mot de passe incorrect.',
            })

        return _json_response({
            'success': True,
            'data': {
                'id': utilisateur.id,
                'client_id': utilisateur.client_id,
                'nom_complet': utilisateur.nom_complet,
                'email': utilisateur.email,
                'role': utilisateur.role,
            },
        })

    # --- Récupérer un profil ---
    @http.route('/api/utilisateur/<int:utilisateur_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_profile(self, utilisateur_id, **kwargs):
        """Récupérer le profil d'un utilisateur par son ID."""
        utilisateur = request.env['custom.utilisateur'].sudo().browse(utilisateur_id)
        if not utilisateur.exists():
            return _json_response({
                'success': False,
                'error': 'Utilisateur introuvable.',
            })

        return _json_response({
            'success': True,
            'data': {
                'id': utilisateur.id,
                'client_id': utilisateur.client_id,
                'nom': utilisateur.nom,
                'prenom': utilisateur.prenom,
                'nom_complet': utilisateur.nom_complet,
                'email': utilisateur.email,
                'role': utilisateur.role,
                'active': utilisateur.active,
            },
        })

    # --- Modifier un profil ---
    @http.route('/api/utilisateur/<int:utilisateur_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_profile(self, utilisateur_id, **kwargs):
        """Modifier le profil d'un utilisateur."""
        utilisateur = request.env['custom.utilisateur'].sudo().browse(utilisateur_id)
        if not utilisateur.exists():
            return _json_response({
                'success': False,
                'error': 'Utilisateur introuvable.',
            })

        body, error = _read_json_body()
        if error:
            return error

        updatable_fields = ['nom', 'prenom', 'email']
        vals = {k: body[k] for k in updatable_fields if k in body}

        if vals:
            utilisateur.write(vals)

        # Mise à jour du mot de passe si fourni
        if body.get('mot_de_passe'):
            utilisateur.set_mot_de_passe(body['mot_de_passe'])

        return _json_response({
            'success': True,
            'data': {
                'id': utilisateur.id,
                'nom_complet': utilisateur.nom_complet,
                'email': utilisateur.email,
            },
        })

    # --- Lister les utilisateurs ---
    @http.route('/api/utilisateur/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_users(self, **kwargs):
        """Lister les utilisateurs, filtrable par rôle."""
        body, error = _read_json_body()
        if error:
            return error

        domain = []
        if body.get('role'):
            domain.append(('role', '=', body['role']))

        utilisateurs = request.env['custom.utilisateur'].sudo().search(domain)
        data = []
        for u in utilisateurs:
            data.append({
                'id': u.id,
                'client_id': u.client_id,
                'nom_complet': u.nom_complet,
                'email': u.email,
                'role': u.role,
            })

        return _json_response({
            'success': True,
            'data': data,
            'count': len(data),
        })
