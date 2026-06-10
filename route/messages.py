from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models import Conversation, Message, Utilisateur

messages_bp = Blueprint('messages', __name__)


# ──────────────────────────────────────────────
#  PAGE MESSAGERIE
# ──────────────────────────────────────────────
@messages_bp.route('/messages')
@login_required
def page_messages():
    conversations = _mes_conversations()
    return render_template('messages.html',
                           user=current_user,
                           conversations=conversations)


# ──────────────────────────────────────────────
#  API — liste des conversations
# ──────────────────────────────────────────────
@messages_bp.route('/api/messages/conversations')
@login_required
def api_conversations():
    conversations = _mes_conversations()
    result = []
    for conv in conversations:
        autre = conv.autre_participant(current_user.id)
        dernier_msg = conv.messages[-1] if conv.messages else None
        non_lus = Message.query.filter_by(
            conversation_id=conv.id, lu=False
        ).filter(Message.user_id != current_user.id).count()

        result.append({
            'id':          conv.id,
            'autre_user':  autre.to_dict(),
            'non_lus':     non_lus,
            'dernier_msg': dernier_msg.to_dict() if dernier_msg else None
        })
    return jsonify(result)


# ──────────────────────────────────────────────
#  API — ouvrir / créer une conversation
# ──────────────────────────────────────────────
@messages_bp.route('/api/messages/conversation/<int:user_id>', methods=['GET'])
@login_required
def ouvrir_conversation(user_id):
    if user_id == current_user.id:
        return jsonify({'erreur': 'Impossible de vous écrire à vous-même.'}), 400

    autre_user = Utilisateur.query.get_or_404(user_id)

    # Garantir l'ordre pour respecter la contrainte unique (plus petit id = user1)
    u1 = min(current_user.id, user_id)
    u2 = max(current_user.id, user_id)

    conv = Conversation.query.filter_by(user1_id=u1, user2_id=u2).first()
    if not conv:
        conv = Conversation(user1_id=u1, user2_id=u2)
        db.session.add(conv)
        db.session.commit()

    # Marquer les messages de l'autre comme lus
    Message.query.filter_by(
        conversation_id=conv.id
    ).filter(Message.user_id != current_user.id).update({'lu': True})
    db.session.commit()

    msgs = [m.to_dict() for m in conv.messages]

    return jsonify({
        'conversation_id': conv.id,
        'autre_user':      autre_user.to_dict(),
        'messages':        msgs
    })


# ──────────────────────────────────────────────
#  API — envoyer un message
# ──────────────────────────────────────────────
@messages_bp.route('/api/messages/envoyer', methods=['POST'])
@login_required
def envoyer_message():
    data            = request.get_json()
    conversation_id = data.get('conversation_id')
    contenu         = (data.get('contenu') or '').strip()

    if not contenu:
        return jsonify({'erreur': 'Le message est vide.'}), 400

    # Vérifier que l'utilisateur appartient à la conversation
    conv = Conversation.query.get_or_404(conversation_id)
    if current_user.id not in (conv.user1_id, conv.user2_id):
        return jsonify({'erreur': 'Non autorisé.'}), 403

    msg = Message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        contenu=contenu
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({'succes': True, 'message': msg.to_dict()}), 201


# ──────────────────────────────────────────────
#  API — nombre de messages non lus (pour badge)
# ──────────────────────────────────────────────
@messages_bp.route('/api/messages/non-lus')
@login_required
def messages_non_lus():
    count = Message.query.join(Conversation).filter(
        (Conversation.user1_id == current_user.id) | (Conversation.user2_id == current_user.id),
        Message.user_id != current_user.id,
        Message.lu == False
    ).count()
    return jsonify({'count': count})


# ──────────────────────────────────────────────
#  HELPER INTERNE
# ──────────────────────────────────────────────
def _mes_conversations():
    """Retourne toutes les conversations de l'utilisateur, triées par dernière activité."""
    return Conversation.query.filter(
        (Conversation.user1_id == current_user.id) |
        (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.date_creation.desc()).all()
