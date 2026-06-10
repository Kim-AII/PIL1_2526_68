from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Utilisateur, UserCompetence, Competence, Disponibilite
from datetime import datetime

users_bp = Blueprint('users', __name__)


# ──────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────
@users_bp.route('/')
@users_bp.route('/dashboard')
@login_required
def dashboard():
    # Imports locaux pour éviter les imports circulaires
    from routes.matching import generer_suggestions
    from models import Message, Conversation, Matching, SeanceMentorat, OffreMentorat

    uid = current_user.id

    # 1. Top 3 suggestions de matching
    suggestions = generer_suggestions(current_user)[:3]

    # 2. Nombre de messages non lus
    nb_messages = Message.query.join(Conversation).filter(
        (Conversation.user1_id == uid) | (Conversation.user2_id == uid),
        Message.user_id != uid,
        Message.lu == False
    ).count()

    # 3. Nombre de compétences renseignées
    nb_competences = len(current_user.competences)

    # 4. Matchings acceptés (sessions actives)
    nb_matchings = Matching.query.filter(
        (Matching.mentor_id == uid) | (Matching.mentore_id == uid),
        Matching.statut == 'accepte'
    ).count()

    # 4b. Séances de mentorat planifiées/confirmées
    nb_seances = SeanceMentorat.query.filter(
        (SeanceMentorat.mentor_id == uid) | (SeanceMentorat.mentore_id == uid),
        SeanceMentorat.statut.in_(['planifiee', 'confirmee'])
    ).count()

    # 4c. Publications (offres/demandes) récentes compatibles (3 dernières)
    offres_recentes = OffreMentorat.query.filter(
        OffreMentorat.statut == 'ouverte',
        OffreMentorat.auteur_id != uid
    ).order_by(OffreMentorat.date_creation.desc()).limit(3).all()

    # 5. Conversations récentes (3 dernières)
    convs_recentes = Conversation.query.filter(
        (Conversation.user1_id == uid) | (Conversation.user2_id == uid)
    ).order_by(Conversation.date_creation.desc()).limit(3).all()

    # 6. Score de complétion du profil (calculé ici, plus propre que dans le template)
    completion = 0
    if current_user.nom and current_user.prenom:   completion += 20
    if current_user.filiere and current_user.niveau: completion += 20
    if current_user.bio:                             completion += 20
    if nb_competences > 0:                           completion += 20
    if current_user.disponibilites:                  completion += 20

    return render_template('dashboard.html',
                           suggestions=suggestions,
                           nb_messages=nb_messages,
                           nb_competences=nb_competences,
                           nb_matchings=nb_matchings,
                           nb_seances=nb_seances,
                           offres_recentes=offres_recentes,
                           convs_recentes=convs_recentes,
                           completion=completion)


# ──────────────────────────────────────────────
#  PROFIL — affichage
# ──────────────────────────────────────────────
@users_bp.route('/profil')
@login_required
def profil():
    toutes_competences = Competence.query.order_by(Competence.categorie, Competence.nom).all()
    return render_template('profil.html',
                           user=current_user,
                           toutes_competences=toutes_competences)


# ──────────────────────────────────────────────
#  PROFIL — modification
# ──────────────────────────────────────────────
@users_bp.route('/profil/modifier', methods=['POST'])
@login_required
def modifier_profil():
    data = request.form

    current_user.nom     = data.get('nom',     current_user.nom).strip()
    current_user.prenom  = data.get('prenom',  current_user.prenom).strip()
    current_user.filiere = data.get('filiere', current_user.filiere)
    current_user.niveau  = data.get('niveau',  current_user.niveau)
    current_user.bio     = data.get('bio',     current_user.bio)

    # Changement de mot de passe (facultatif)
    nouveau_mdp  = data.get('nouveau_mot_de_passe', '').strip()
    confirmer    = data.get('confirmer_mot_de_passe', '').strip()

    if nouveau_mdp:
        if nouveau_mdp != confirmer:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('users.profil'))
        if len(nouveau_mdp) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'danger')
            return redirect(url_for('users.profil'))
        current_user.set_password(nouveau_mdp)

    db.session.commit()
    flash('Profil mis à jour avec succès.', 'success')
    return redirect(url_for('users.profil'))


# ──────────────────────────────────────────────
#  COMPÉTENCES — ajouter / modifier
# ──────────────────────────────────────────────
@users_bp.route('/api/profil/competences', methods=['POST'])
@login_required
def ajouter_competence():
    data          = request.get_json()
    competence_id = data.get('competence_id')
    type_comp     = data.get('type')   # 'fort' ou 'faible'

    if not competence_id or type_comp not in ('fort', 'faible'):
        return jsonify({'erreur': 'Données invalides.'}), 400

    existing = UserCompetence.query.filter_by(
        user_id=current_user.id, competence_id=competence_id
    ).first()

    if existing:
        existing.type = type_comp
    else:
        uc = UserCompetence(user_id=current_user.id,
                            competence_id=competence_id,
                            type=type_comp)
        db.session.add(uc)

    db.session.commit()
    return jsonify({'succes': True})


# ──────────────────────────────────────────────
#  COMPÉTENCES — supprimer
# ──────────────────────────────────────────────
@users_bp.route('/api/profil/competences/<int:competence_id>', methods=['DELETE'])
@login_required
def supprimer_competence(competence_id):
    uc = UserCompetence.query.filter_by(
        user_id=current_user.id, competence_id=competence_id
    ).first_or_404()
    db.session.delete(uc)
    db.session.commit()
    return jsonify({'succes': True})


# ──────────────────────────────────────────────
#  DISPONIBILITÉS — ajouter
# ──────────────────────────────────────────────
@users_bp.route('/api/profil/disponibilites', methods=['POST'])
@login_required
def ajouter_disponibilite():
    data = request.get_json()
    jour = data.get('jour')
    hd   = data.get('heure_debut')
    hf   = data.get('heure_fin')

    if not all([jour, hd, hf]):
        return jsonify({'erreur': 'Champs manquants.'}), 400

    # Convertir les chaînes HH:MM en objets time
    try:
        heure_debut = datetime.strptime(hd, '%H:%M').time()
        heure_fin   = datetime.strptime(hf, '%H:%M').time()
    except ValueError:
        return jsonify({'erreur': 'Format heure invalide (HH:MM).'}), 400

    if heure_debut >= heure_fin:
        return jsonify({'erreur': 'L\'heure de fin doit être après l\'heure de début.'}), 400

    dispo = Disponibilite(
        user_id=current_user.id,
        jour=jour,
        heure_debut=heure_debut,
        heure_fin=heure_fin
    )
    db.session.add(dispo)
    db.session.commit()
    return jsonify({'succes': True, 'id': dispo.id})


# ──────────────────────────────────────────────
#  DISPONIBILITÉS — supprimer
# ──────────────────────────────────────────────
@users_bp.route('/api/profil/disponibilites/<int:dispo_id>', methods=['DELETE'])
@login_required
def supprimer_disponibilite(dispo_id):
    dispo = Disponibilite.query.filter_by(
        id=dispo_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(dispo)
    db.session.commit()
    return jsonify({'succes': True})


# ──────────────────────────────────────────────
#  API — liste des compétences disponibles
# ──────────────────────────────────────────────
@users_bp.route('/api/competences')
@login_required
def liste_competences():
    competences = Competence.query.order_by(Competence.categorie, Competence.nom).all()
    return jsonify([c.to_dict() for c in competences])


# ──────────────────────────────────────────────
#  API — profil d'un utilisateur (public)
# ──────────────────────────────────────────────
@users_bp.route('/api/utilisateur/<int:user_id>')
@login_required
def get_utilisateur(user_id):
    user = Utilisateur.query.get_or_404(user_id)
    data = user.to_dict()
    data['competences'] = [
        {'nom': uc.competence.nom, 'type': uc.type}
        for uc in user.competences
    ]
    data['disponibilites'] = [d.to_dict() for d in user.disponibilites]
    return jsonify(data)
 
 # ──────────────────────────────────────────────
#  PROFIL — voir le profil d'un autre utilisateur
# ──────────────────────────────────────────────
@users_bp.route('/utilisateur/<int:user_id>')
@login_required
def voir_profil(user_id):
    """Page HTML du profil d'un autre utilisateur (lecture seule)."""
    profil = Utilisateur.query.get_or_404(user_id)

    # Score de compatibilité avec l'utilisateur connecté
    from routes.matching import calculer_score
    score = calculer_score(profil, current_user)

    # Compétences communes
    from routes.matching import get_competences_communes, get_dispos_communes
    competences_communes   = get_competences_communes(profil, current_user)
    disponibilites_communes = get_dispos_communes(profil, current_user)

    return render_template('voir_profil.html',
                           profil=profil,
                           score=score,
                           competences_communes=competences_communes,
                           disponibilites_communes=disponibilites_communes)