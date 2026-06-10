from flask import Blueprint, request, jsonify, render_template, abort
from flask_login import login_required, current_user
from extensions import db
from models import (Utilisateur, Competence, OffreMentorat,
                    CandidatureOffre, SeanceMentorat)
from datetime import datetime

mentorat_bp = Blueprint('mentorat', __name__)


# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────

def _score_compat(offre, user):
    """
    Calcule un score de compatibilité simple (0–100) entre une offre/demande
    et l'utilisateur connecté (sans restriction, juste indicatif).
    """
    from routes.matching import calculer_score
    auteur = offre.auteur
    if offre.type_publication == 'offre':
        # L'auteur serait mentor de l'utilisateur connecté
        return calculer_score(auteur, user)
    else:
        # L'auteur cherche un mentor → l'utilisateur connecté serait mentor
        return calculer_score(user, auteur)


def _offre_to_dict_with_score(offre, user):
    d = offre.to_dict()
    d['score_compat'] = _score_compat(offre, user)
    # Indique si l'utilisateur a déjà postulé
    cand = CandidatureOffre.query.filter_by(
        offre_id=offre.id, candidat_id=user.id
    ).first()
    d['ma_candidature'] = cand.to_dict() if cand else None
    return d


# ──────────────────────────────────────────────
#  PAGES HTML
# ──────────────────────────────────────────────

@mentorat_bp.route('/mentorat')
@login_required
def page_mentorat():
    """Page principale : offres et demandes de mentorat."""
    competences = Competence.query.order_by(Competence.categorie, Competence.nom).all()
    return render_template('mentorat_offres.html',
                           user=current_user,
                           competences=competences)


@mentorat_bp.route('/mentorat/seances')
@login_required
def page_seances():
    """Page de mes séances de mentorat."""
    uid = current_user.id
    seances_avenir = SeanceMentorat.query.filter(
        (SeanceMentorat.mentor_id == uid) | (SeanceMentorat.mentore_id == uid),
        SeanceMentorat.statut.in_(['planifiee', 'confirmee'])
    ).order_by(SeanceMentorat.date_seance.asc()).all()

    seances_passees = SeanceMentorat.query.filter(
        (SeanceMentorat.mentor_id == uid) | (SeanceMentorat.mentore_id == uid),
        SeanceMentorat.statut.in_(['terminee', 'annulee'])
    ).order_by(SeanceMentorat.date_seance.desc()).limit(20).all()

    return render_template('mentorat_seances.html',
                           user=current_user,
                           seances_avenir=seances_avenir,
                           seances_passees=seances_passees)


# ──────────────────────────────────────────────
#  API — lister les offres/demandes disponibles
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/offres')
@login_required
def api_liste_offres():
    """
    Retourne les offres/demandes ouvertes, excluant celles de l'utilisateur connecté.
    Paramètres GET : type (offre|demande), filiere, niveau, competence_id
    """
    type_pub   = request.args.get('type')       # 'offre' | 'demande' | None (tous)
    filiere    = request.args.get('filiere')
    niveau     = request.args.get('niveau')
    comp_id    = request.args.get('competence_id', type=int)

    q = OffreMentorat.query.filter(
        OffreMentorat.statut == 'ouverte',
        OffreMentorat.auteur_id != current_user.id
    )

    if type_pub in ('offre', 'demande'):
        q = q.filter(OffreMentorat.type_publication == type_pub)
    if filiere:
        q = q.filter(OffreMentorat.filiere_cible == filiere)
    if niveau:
        q = q.filter(OffreMentorat.niveau_cible == niveau)
    if comp_id:
        q = q.filter(OffreMentorat.competence_id == comp_id)

    offres = q.order_by(OffreMentorat.date_creation.desc()).all()

    result = []
    for o in offres:
        # Masquer les offres complètes (plus de places)
        if o.places_restantes <= 0:
            continue
        result.append(_offre_to_dict_with_score(o, current_user))

    # Trier par score décroissant
    result.sort(key=lambda x: x['score_compat'], reverse=True)
    return jsonify(result)


# ──────────────────────────────────────────────
#  API — mes publications
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/mes-publications')
@login_required
def api_mes_publications():
    """Mes offres/demandes publiées avec leurs candidatures."""
    offres = OffreMentorat.query.filter_by(
        auteur_id=current_user.id
    ).order_by(OffreMentorat.date_creation.desc()).all()

    result = []
    for o in offres:
        d = o.to_dict()
        d['candidatures'] = [c.to_dict() for c in o.candidatures]
        result.append(d)
    return jsonify(result)


# ──────────────────────────────────────────────
#  API — créer une offre ou demande
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/offres', methods=['POST'])
@login_required
def api_creer_offre():
    data = request.get_json()

    type_pub = data.get('type_publication')
    titre    = (data.get('titre') or '').strip()

    if type_pub not in ('offre', 'demande'):
        return jsonify({'erreur': 'type_publication invalide (offre ou demande).'}), 400
    if not titre:
        return jsonify({'erreur': 'Le titre est requis.'}), 400

    max_p = int(data.get('max_places', 1))
    if max_p < 1 or max_p > 20:
        return jsonify({'erreur': 'max_places doit être entre 1 et 20.'}), 400

    offre = OffreMentorat(
        auteur_id        = current_user.id,
        type_publication = type_pub,
        titre            = titre,
        description      = (data.get('description') or '').strip() or None,
        competence_id    = data.get('competence_id') or None,
        niveau_cible     = data.get('niveau_cible') or None,
        filiere_cible    = data.get('filiere_cible') or None,
        max_places       = max_p
    )
    db.session.add(offre)
    db.session.commit()
    return jsonify({'succes': True, 'offre': offre.to_dict()}), 201


# ──────────────────────────────────────────────
#  API — modifier une publication
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/offres/<int:offre_id>', methods=['PUT'])
@login_required
def api_modifier_offre(offre_id):
    offre = OffreMentorat.query.get_or_404(offre_id)
    if offre.auteur_id != current_user.id:
        return jsonify({'erreur': 'Non autorisé.'}), 403

    data = request.get_json()
    if 'titre' in data and data['titre'].strip():
        offre.titre = data['titre'].strip()
    if 'description' in data:
        offre.description = data['description']
    if 'niveau_cible' in data:
        offre.niveau_cible = data['niveau_cible'] or None
    if 'filiere_cible' in data:
        offre.filiere_cible = data['filiere_cible'] or None
    if 'competence_id' in data:
        offre.competence_id = data['competence_id'] or None
    if 'max_places' in data:
        offre.max_places = max(1, int(data['max_places']))
    if 'statut' in data and data['statut'] in ('ouverte', 'fermee', 'archivee'):
        offre.statut = data['statut']

    db.session.commit()
    return jsonify({'succes': True, 'offre': offre.to_dict()})


# ──────────────────────────────────────────────
#  API — fermer/archiver une publication
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/offres/<int:offre_id>', methods=['DELETE'])
@login_required
def api_fermer_offre(offre_id):
    offre = OffreMentorat.query.get_or_404(offre_id)
    if offre.auteur_id != current_user.id:
        return jsonify({'erreur': 'Non autorisé.'}), 403

    offre.statut = 'archivee'
    db.session.commit()
    return jsonify({'succes': True})


# ──────────────────────────────────────────────
#  API — postuler / répondre à une publication
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/offres/<int:offre_id>/postuler', methods=['POST'])
@login_required
def api_postuler(offre_id):
    offre = OffreMentorat.query.get_or_404(offre_id)

    if offre.auteur_id == current_user.id:
        return jsonify({'erreur': 'Vous ne pouvez pas postuler à votre propre publication.'}), 400
    if offre.statut != 'ouverte':
        return jsonify({'erreur': 'Cette publication est fermée.'}), 400
    if offre.places_restantes <= 0:
        return jsonify({'erreur': 'Plus de places disponibles.'}), 400

    # Vérifier doublon
    existing = CandidatureOffre.query.filter_by(
        offre_id=offre_id, candidat_id=current_user.id
    ).first()
    if existing:
        return jsonify({'erreur': 'Vous avez déjà postulé à cette publication.'}), 409

    data    = request.get_json() or {}
    message = (data.get('message') or '').strip() or None

    cand = CandidatureOffre(
        offre_id    = offre_id,
        candidat_id = current_user.id,
        message     = message
    )
    db.session.add(cand)
    db.session.commit()
    return jsonify({'succes': True, 'candidature': cand.to_dict()}), 201


# ──────────────────────────────────────────────
#  API — accepter ou refuser une candidature
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/candidatures/<int:cand_id>/repondre', methods=['POST'])
@login_required
def api_repondre_candidature(cand_id):
    cand  = CandidatureOffre.query.get_or_404(cand_id)
    offre = cand.offre

    if offre.auteur_id != current_user.id:
        return jsonify({'erreur': 'Non autorisé.'}), 403

    data   = request.get_json()
    action = data.get('action')  # 'accepter' | 'refuser'

    if action not in ('accepter', 'refuser'):
        return jsonify({'erreur': 'Action invalide.'}), 400

    if action == 'refuser':
        cand.statut = 'refusee'
        db.session.commit()
        return jsonify({'succes': True, 'statut': 'refusee'})

    # ── Acceptation ──
    if offre.places_restantes <= 0:
        return jsonify({'erreur': 'Plus de places disponibles.'}), 400

    cand.statut = 'acceptee'

    # Déterminer mentor et mentoré selon le type de publication
    if offre.type_publication == 'offre':
        # L'auteur est mentor, le candidat est mentoré
        mentor_id  = offre.auteur_id
        mentore_id = cand.candidat_id
    else:
        # L'auteur cherche un mentor, le candidat est mentor
        mentor_id  = cand.candidat_id
        mentore_id = offre.auteur_id

    seance = SeanceMentorat(
        offre_id       = offre.id,
        candidature_id = cand.id,
        mentor_id      = mentor_id,
        mentore_id     = mentore_id
    )
    db.session.add(seance)

    # Fermer l'offre si plus de places
    db.session.flush()   # pour recalculer nb_acceptees
    if offre.places_restantes <= 0:
        offre.statut = 'fermee'

    db.session.commit()
    return jsonify({'succes': True, 'statut': 'acceptee', 'seance': seance.to_dict()})


# ──────────────────────────────────────────────
#  API — mes séances
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/seances')
@login_required
def api_mes_seances():
    uid = current_user.id
    seances = SeanceMentorat.query.filter(
        (SeanceMentorat.mentor_id == uid) | (SeanceMentorat.mentore_id == uid)
    ).order_by(SeanceMentorat.date_seance.asc().nullslast()).all()
    return jsonify([s.to_dict() for s in seances])


# ──────────────────────────────────────────────
#  API — mettre à jour une séance
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/seances/<int:seance_id>', methods=['PUT'])
@login_required
def api_update_seance(seance_id):
    seance = SeanceMentorat.query.get_or_404(seance_id)
    uid    = current_user.id

    if seance.mentor_id != uid and seance.mentore_id != uid:
        return jsonify({'erreur': 'Non autorisé.'}), 403

    data = request.get_json()

    # Mise à jour du statut
    nouveau_statut = data.get('statut')
    if nouveau_statut:
        statuts_valides = ('planifiee', 'confirmee', 'terminee', 'annulee')
        if nouveau_statut not in statuts_valides:
            return jsonify({'erreur': 'Statut invalide.'}), 400
        seance.statut = nouveau_statut

    # Mise à jour des détails (date, lieu, durée, notes)
    if 'date_seance' in data and data['date_seance']:
        try:
            seance.date_seance = datetime.fromisoformat(data['date_seance'])
        except ValueError:
            return jsonify({'erreur': 'Format de date invalide (ISO 8601).'}), 400
    if 'lieu' in data:
        seance.lieu = data['lieu'] or None
    if 'duree_minutes' in data:
        seance.duree_minutes = max(15, int(data['duree_minutes']))
    if 'notes' in data:
        seance.notes = data['notes'] or None

    db.session.commit()
    return jsonify({'succes': True, 'seance': seance.to_dict()})


# ──────────────────────────────────────────────
#  API — stats pour le dashboard
# ──────────────────────────────────────────────

@mentorat_bp.route('/api/mentorat/stats')
@login_required
def api_stats():
    uid = current_user.id
    nb_seances = SeanceMentorat.query.filter(
        (SeanceMentorat.mentor_id == uid) | (SeanceMentorat.mentore_id == uid),
        SeanceMentorat.statut.in_(['planifiee', 'confirmee'])
    ).count()
    nb_publications = OffreMentorat.query.filter_by(
        auteur_id=uid, statut='ouverte'
    ).count()
    nb_candidatures_recues = CandidatureOffre.query.join(OffreMentorat).filter(
        OffreMentorat.auteur_id == uid,
        CandidatureOffre.statut == 'en_attente'
    ).count()
    return jsonify({
        'nb_seances':             nb_seances,
        'nb_publications':        nb_publications,
        'nb_candidatures_recues': nb_candidatures_recues
    })
