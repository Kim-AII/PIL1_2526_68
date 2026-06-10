from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models import Utilisateur, Matching

matching_bp = Blueprint('matching', __name__)


# ──────────────────────────────────────────────
#  ALGORITHME DE MATCHING
# ──────────────────────────────────────────────

POIDS_COMPETENCES = 0.50   # 50%
POIDS_HORAIRES    = 0.30   # 30%
POIDS_FILIERE     = 0.20   # 20%

NIVEAUX_ORDRE = {'L1': 1, 'L2': 2, 'L3': 3, 'M1': 4, 'M2': 5}


def score_competences(mentor, mentore):
    """
    Score basé sur la couverture des lacunes du mentoré par les points forts du mentor.
    """
    forts_mentor    = {uc.competence_id for uc in mentor.competences  if uc.type == 'fort'}
    faibles_mentore = {uc.competence_id for uc in mentore.competences if uc.type == 'faible'}

    if not faibles_mentore:
        return 0.0   # Pas de lacunes déclarées → pas de score

    couverts = len(forts_mentor & faibles_mentore)
    return couverts / len(faibles_mentore)


def score_horaires(mentor, mentore):
    """
    Score basé sur le chevauchement des disponibilités.
    """
    def creneaux(user):
        return {(d.jour, str(d.heure_debut), str(d.heure_fin)) for d in user.disponibilites}

    dispos_mentor   = creneaux(mentor)
    dispos_mentore  = creneaux(mentore)

    if not dispos_mentor or not dispos_mentore:
        return 0.0   # Aucune dispo renseignée

    communs = len(dispos_mentor & dispos_mentore)
    total   = len(dispos_mentor | dispos_mentore)
    return communs / total if total > 0 else 0.0


def score_filiere_niveau(mentor, mentore):
    """
    Score basé sur la proximité de filière et de niveau.
    Répartition : filière 0.5 / niveau 0.5 (dans les 20% globaux).
    """
    score = 0.0

    if mentor.filiere and mentore.filiere:
        if mentor.filiere == mentore.filiere:
            score += 0.5

    niv_m  = NIVEAUX_ORDRE.get(mentor.niveau,  0)
    niv_me = NIVEAUX_ORDRE.get(mentore.niveau, 0)

    if niv_m and niv_me:
        diff = abs(niv_m - niv_me)
        if diff == 0:
            score += 0.5
        elif diff == 1:
            score += 0.25   # Niveaux adjacents : bonus partiel

    return score


def calculer_score(mentor, mentore):
    """Score global entre 0 et 100."""
    s = (
        score_competences(mentor, mentore) * POIDS_COMPETENCES +
        score_horaires(mentor, mentore)    * POIDS_HORAIRES    +
        score_filiere_niveau(mentor, mentore) * POIDS_FILIERE
    )
    return round(s * 100, 1)   # En pourcentage, 1 décimale


def get_competences_communes(mentor, mentore):
    """Liste des compétences que le mentor maîtrise et dont le mentoré a besoin."""
    forts_mentor    = {uc.competence_id: uc.competence for uc in mentor.competences  if uc.type == 'fort'}
    faibles_mentore = {uc.competence_id              for uc in mentore.competences if uc.type == 'faible'}
    return [
        {'id': comp.id, 'nom': comp.nom}
        for cid, comp in forts_mentor.items()
        if cid in faibles_mentore
    ]


def get_dispos_communes(mentor, mentore):
    """Créneaux horaires en commun."""
    def creneaux(user):
        return {(d.jour, str(d.heure_debut), str(d.heure_fin)) for d in user.disponibilites}
    communs = creneaux(mentor) & creneaux(mentore)
    return [{'jour': c[0], 'heure_debut': c[1], 'heure_fin': c[2]} for c in sorted(communs)]


def generer_suggestions(user, limite=10):
    """
    Génère la liste des mentors potentiels classés par score décroissant.
    Exclut l'utilisateur lui-même.
    """
    candidats = Utilisateur.query.filter(Utilisateur.id != user.id).all()
    resultats = []

    for candidat in candidats:
        score = calculer_score(candidat, user)   # candidat = mentor potentiel
        if score > 0:
            resultats.append({
                'user':                   candidat.to_dict(),
                'score':                  score,
                'competences_communes':   get_competences_communes(candidat, user),
                'disponibilites_communes': get_dispos_communes(candidat, user)
            })

    resultats.sort(key=lambda x: x['score'], reverse=True)
    return resultats[:limite]


# ──────────────────────────────────────────────
#  PAGE MATCHING
# ──────────────────────────────────────────────
@matching_bp.route('/matching')
@login_required
def page_matching():
    suggestions = generer_suggestions(current_user)
    return render_template('matching.html', user=current_user, suggestions=suggestions)


# ──────────────────────────────────────────────
#  API — suggestions (JSON)
# ──────────────────────────────────────────────
@matching_bp.route('/api/matching/suggestions')
@login_required
def api_suggestions():
    suggestions = generer_suggestions(current_user)
    return jsonify(suggestions)


# ──────────────────────────────────────────────
#  API — contacter un mentor (crée un matching)
# ──────────────────────────────────────────────
@matching_bp.route('/api/matching/contacter', methods=['POST'])
@login_required
def contacter_mentor():
    data      = request.get_json()
    mentor_id = data.get('mentor_id')

    if not mentor_id:
        return jsonify({'erreur': 'mentor_id requis.'}), 400

    mentor = Utilisateur.query.get_or_404(mentor_id)

    # Éviter les doublons
    existing = Matching.query.filter_by(
        mentor_id=mentor.id, mentore_id=current_user.id, statut='en_attente'
    ).first()
    if existing:
        return jsonify({'erreur': 'Demande déjà envoyée.'}), 409

    score   = calculer_score(mentor, current_user)
    match   = Matching(mentor_id=mentor.id, mentore_id=current_user.id, score=score)
    db.session.add(match)
    db.session.commit()

    return jsonify({'succes': True, 'matching_id': match.id, 'score': score})


# ──────────────────────────────────────────────
#  API — répondre à une demande de matching
# ──────────────────────────────────────────────
@matching_bp.route('/api/matching/<int:matching_id>/repondre', methods=['POST'])
@login_required
def repondre_matching(matching_id):
    match  = Matching.query.get_or_404(matching_id)
    action = request.get_json().get('action')   # 'accepter' ou 'refuser'

    if match.mentor_id != current_user.id:
        return jsonify({'erreur': 'Non autorisé.'}), 403

    if action == 'accepter':
        match.statut = 'accepte'
    elif action == 'refuser':
        match.statut = 'refuse'
    else:
        return jsonify({'erreur': 'Action invalide.'}), 400

    db.session.commit()
    return jsonify({'succes': True, 'statut': match.statut})


# ──────────────────────────────────────────────
#  API — mes demandes reçues (en tant que mentor)
# ──────────────────────────────────────────────
@matching_bp.route('/api/matching/demandes')
@login_required
def mes_demandes():
    demandes = Matching.query.filter_by(
        mentor_id=current_user.id, statut='en_attente'
    ).all()
    return jsonify([{
        'id':        d.id,
        'mentore':   d.mentore.to_dict(),
        'score':     d.score,
        'date':      d.date_creation.isoformat()
    } for d in demandes])
