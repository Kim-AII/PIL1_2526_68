# ================================================================
# IFRI MentorLink - Module Messagerie
# Fichier : messagerie/messages.py
# Auteur  : Sandrine HOUNTON
# ================================================================

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from extensions import db, socketio
from models import Utilisateur
from datetime import datetime

messages_bp = Blueprint('messages', __name__)


# ================================================================
# MODELES (Conversation et Message)
# A ajouter dans models.py si pas encore fait
# ================================================================
#
# class Conversation(db.Model):
#     __tablename__ = 'conversations'
#     id            = db.Column(db.Integer, primary_key=True)
#     user1_id      = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
#     user2_id      = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
#     date_creation = db.Column(db.DateTime, default=datetime.utcnow)
#     messages      = db.relationship('Message', backref='conversation', lazy=True, order_by='Message.date_envoi')
#     user1         = db.relationship('Utilisateur', foreign_keys=[user1_id])
#     user2         = db.relationship('Utilisateur', foreign_keys=[user2_id])
#
#     def autre_participant(self, user_id):
#         return self.user2 if self.user1_id == user_id else self.user1
#
#     def to_dict(self, current_id):
#         autre = self.autre_participant(current_id)
#         return {
#             'id': self.id,
#             'autre_user': autre.to_dict(),
#             'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M:%S')
#         }
#
#
# class Message(db.Model):
#     __tablename__ = 'messages'
#     id              = db.Column(db.Integer, primary_key=True)
#     conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
#     user_id         = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
#     contenu         = db.Column(db.Text, nullable=False)
#     date_envoi      = db.Column(db.DateTime, default=datetime.utcnow)
#     lu              = db.Column(db.Boolean, default=False)
#     auteur          = db.relationship('Utilisateur', foreign_keys=[user_id])
#
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'conversation_id': self.conversation_id,
#             'user_id': self.user_id,
#             'auteur': f"{self.auteur.prenom} {self.auteur.nom}",
#             'contenu': self.contenu,
#             'date_envoi': self.date_envoi.strftime('%Y-%m-%d %H:%M:%S'),
#             'lu': self.lu
#         }

# ================================================================
# Import des modèles (décommenter après avoir ajouté dans models.py)
# ================================================================
from models import Conversation, Message


# ================================================================
# PAGE PRINCIPALE MESSAGERIE
# ================================================================

@messages_bp.route('/messages')
@login_required
def page_messages():
    conversations = _mes_conversations()
    return render_template(
        'messages.html',
        user=current_user,
        conversations=conversations
    )


# ================================================================
# API — Liste des conversations
# ================================================================

@messages_bp.route('/api/messages/conversations')
@login_required
def api_conversations():
    conversations = _mes_conversations()
    result = []
    for conv in conversations:
        autre = conv.autre_participant(current_user.id)
        dernier_msg = conv.messages[-1] if conv.messages else None
        non_lus = Message.query.filter_by(
            conversation_id=conv.id,
            lu=False
        ).filter(Message.user_id != current_user.id).count()

        result.append({
            'id': conv.id,
            'autre_user': autre.to_dict(),
            'non_lus': non_lus,
            'dernier_msg': dernier_msg.to_dict() if dernier_msg else None
        })

    return jsonify(result)


# ================================================================
# API — Ouvrir / créer une conversation
# ================================================================

@messages_bp.route('/api/messages/conversation/<int:user_id>', methods=['GET'])
@login_required
def ouvrir_conversation(user_id):
    if user_id == current_user.id:
        return jsonify({'erreur': 'Impossible de vous écrire à vous-même.'}), 400

    autre_user = Utilisateur.query.get_or_404(user_id)

    # Garantir l'ordre pour respecter la contrainte unique
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
    ).filter(
        Message.user_id != current_user.id,
        Message.lu == False
    ).update({'lu': True})
    db.session.commit()

    msgs = [m.to_dict() for m in conv.messages]

    return jsonify({
        'conversation_id': conv.id,
        'autre_user': autre_user.to_dict(),
        'messages': msgs
    })


# ================================================================
# API — Envoyer un message (HTTP)
# ================================================================

@messages_bp.route('/api/messages/envoyer', methods=['POST'])
@login_required
def envoyer_message():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    contenu = (data.get('contenu') or '').strip()

    if not contenu:
        return jsonify({'erreur': 'Le message est vide.'}), 400

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

    # Diffuser via WebSocket en temps réel
    socketio.emit(
        'nouveau_message',
        msg.to_dict(),
        room=f'conv_{conversation_id}'
    )

    # Notifier l'autre utilisateur
    autre_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
    socketio.emit(
        'notification',
        {
            'conversation_id': conversation_id,
            'expediteur': f"{current_user.prenom} {current_user.nom}",
            'apercu': contenu[:60]
        },
        room=f'user_{autre_id}'
    )

    return jsonify({'succes': True, 'message': msg.to_dict()}), 201


# ================================================================
# API — Nombre de messages non lus (badge navbar)
# ================================================================

@messages_bp.route('/api/messages/non-lus')
@login_required
def messages_non_lus():
    count = Message.query.join(Conversation).filter(
        (Conversation.user1_id == current_user.id) | (Conversation.user2_id == current_user.id),
        Message.user_id != current_user.id,
        Message.lu == False
    ).count()
    return jsonify({'count': count})


# ================================================================
# API — Liste des utilisateurs (pour nouvelle conversation)
# ================================================================

@messages_bp.route('/api/messages/utilisateurs')
@login_required
def liste_utilisateurs():
    users = Utilisateur.query.filter(
        Utilisateur.id != current_user.id,
        Utilisateur.est_actif == True
    ).all()
    return jsonify([u.to_dict() for u in users])


# ================================================================
# WEBSOCKET — Rejoindre/quitter une room
# ================================================================

@socketio.on('rejoindre_conversation')
def on_rejoindre(data):
    conv_id = data.get('conversation_id')
    join_room(f'conv_{conv_id}')


@socketio.on('quitter_conversation')
def on_quitter(data):
    conv_id = data.get('conversation_id')
    leave_room(f'conv_{conv_id}')


@socketio.on('connecter_utilisateur')
def on_connecter_user(data):
    user_id = data.get('user_id')
    join_room(f'user_{user_id}')


# ================================================================
# WEBSOCKET — Envoyer un message en temps réel
# ================================================================

@socketio.on('envoyer_message')
def on_envoyer_message(data):
    conv_id = data.get('conversation_id')
    contenu = (data.get('contenu') or '').strip()
    user_id = data.get('user_id')

    if not contenu or not conv_id:
        return

    conv = Conversation.query.get(conv_id)
    if not conv or user_id not in (conv.user1_id, conv.user2_id):
        return

    msg = Message(
        conversation_id=conv_id,
        user_id=user_id,
        contenu=contenu
    )
    db.session.add(msg)
    db.session.commit()

    # Diffuser à tous dans la room
    emit('nouveau_message', msg.to_dict(), room=f'conv_{conv_id}')

    # Notification à l'autre
    autre_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
    auteur = Utilisateur.query.get(user_id)
    emit(
        'notification',
        {
            'conversation_id': conv_id,
            'expediteur': f"{auteur.prenom} {auteur.nom}",
            'apercu': contenu[:60]
        },
        room=f'user_{autre_id}'
    )


# ================================================================
# HELPER INTERNE
# ================================================================

def _mes_conversations():
    """Retourne toutes les conversations de l'utilisateur, triées par dernière activité."""
    return Conversation.query.filter(
        (Conversation.user1_id == current_user.id) |
        (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.date_creation.desc()).all()
