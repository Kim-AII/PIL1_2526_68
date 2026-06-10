from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import Utilisateur

auth_bp = Blueprint('auth', __name__)


# ──────────────────────────────────────────────
#  CONNEXION
# ──────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))

    if request.method == 'POST':
        identifiant  = request.form.get('identifiant', '').strip()
        mot_de_passe = request.form.get('mot_de_passe', '')
        remember_me  = request.form.get('remember_me') == 'on'

        # Recherche par email OU téléphone
        user = (
            Utilisateur.query.filter_by(email=identifiant).first() or
            Utilisateur.query.filter_by(telephone=identifiant).first()
        )

        if user and user.check_password(mot_de_passe):
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('users.dashboard'))

        flash('Identifiant ou mot de passe incorrect.', 'danger')

    return render_template('login.html')


# ──────────────────────────────────────────────
#  INSCRIPTION
# ──────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))

    if request.method == 'POST':
        nom          = request.form.get('nom', '').strip()
        prenom       = request.form.get('prenom', '').strip()
        email        = request.form.get('email', '').strip().lower()
        telephone    = request.form.get('telephone', '').strip()
        mot_de_passe = request.form.get('mot_de_passe', '')
        confirmer    = request.form.get('confirmer', '')
        filiere      = request.form.get('filiere', '')
        niveau       = request.form.get('niveau', '')

        # Validations
        erreurs = []
        if not all([nom, prenom, email, telephone, mot_de_passe]):
            erreurs.append('Tous les champs obligatoires doivent être remplis.')
        if mot_de_passe != confirmer:
            erreurs.append('Les mots de passe ne correspondent pas.')
        if len(mot_de_passe) < 6:
            erreurs.append('Le mot de passe doit contenir au moins 6 caractères.')
        if Utilisateur.query.filter_by(email=email).first():
            erreurs.append('Cette adresse email est déjà utilisée.')
        if Utilisateur.query.filter_by(telephone=telephone).first():
            erreurs.append('Ce numéro de téléphone est déjà utilisé.')

        if erreurs:
            for e in erreurs:
                flash(e, 'danger')
            return render_template('register.html')

        # Création de l'utilisateur
        user = Utilisateur(
            nom=nom, prenom=prenom, email=email,
            telephone=telephone, filiere=filiere, niveau=niveau
        )
        user.set_password(mot_de_passe)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Bienvenue {prenom} ! Votre compte a été créé.', 'success')
        return redirect(url_for('users.profil'))

    return render_template('register.html')


# ──────────────────────────────────────────────
#  DÉCONNEXION
# ──────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))


# ──────────────────────────────────────────────
#  RÉINITIALISATION MOT DE PASSE
# ──────────────────────────────────────────────
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = Utilisateur.query.filter_by(email=email).first()

        # TODO: envoyer un email de réinitialisation (Flask-Mail)
        # Pour l'instant : message générique (sécurité : ne pas révéler si l'email existe)
        flash('Si cet email existe, un lien de réinitialisation a été envoyé.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')
