from extensions import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))


# ──────────────────────────────────────────────
#  UTILISATEUR
# ──────────────────────────────────────────────
class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'

    id               = db.Column(db.Integer, primary_key=True)
    nom              = db.Column(db.String(100), nullable=False)
    prenom           = db.Column(db.String(100), nullable=False)
    email            = db.Column(db.String(150), unique=True, nullable=False)
    telephone        = db.Column(db.String(20),  unique=True, nullable=False)
    mot_de_passe     = db.Column(db.String(255), nullable=False)
    filiere          = db.Column(db.String(20))   # IA, IM, GL, SE_IoT, SI
    niveau           = db.Column(db.String(5))    # L1, L2, L3, M1, M2
    bio              = db.Column(db.Text)
    photo_url        = db.Column(db.String(255))
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    competences    = db.relationship('UserCompetence', backref='utilisateur', lazy=True, cascade='all, delete-orphan')
    disponibilites = db.relationship('Disponibilite',  backref='utilisateur', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.mot_de_passe = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.mot_de_passe, password)

    def to_dict(self):
        return {
            'id':       self.id,
            'nom':      self.nom,
            'prenom':   self.prenom,
            'email':    self.email,
            'filiere':  self.filiere,
            'niveau':   self.niveau,
            'bio':      self.bio,
            'photo_url': self.photo_url
        }

    def __repr__(self):
        return f'<Utilisateur {self.prenom} {self.nom}>'


# ──────────────────────────────────────────────
#  COMPETENCE
# ──────────────────────────────────────────────
class Competence(db.Model):
    __tablename__ = 'competences'

    id        = db.Column(db.Integer, primary_key=True)
    nom       = db.Column(db.String(100), unique=True, nullable=False)
    categorie = db.Column(db.String(50))   # ex : Programmation, Mathématiques…

    def to_dict(self):
        return {'id': self.id, 'nom': self.nom, 'categorie': self.categorie}


# ──────────────────────────────────────────────
#  USER_COMPETENCE  (table de jonction)
# ──────────────────────────────────────────────
class UserCompetence(db.Model):
    __tablename__ = 'user_competences'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    competence_id = db.Column(db.Integer, db.ForeignKey('competences.id'),  nullable=False)
    type          = db.Column(db.String(10), nullable=False)   # 'fort' ou 'faible'

    competence = db.relationship('Competence')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'competence_id', name='unique_user_competence'),
    )


# ──────────────────────────────────────────────
#  DISPONIBILITE
# ──────────────────────────────────────────────
class Disponibilite(db.Model):
    __tablename__ = 'disponibilites'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    jour        = db.Column(db.String(20), nullable=False)   # Lundi, Mardi…
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin   = db.Column(db.Time, nullable=False)

    def to_dict(self):
        return {
            'id':          self.id,
            'jour':        self.jour,
            'heure_debut': str(self.heure_debut),
            'heure_fin':   str(self.heure_fin)
        }


# ──────────────────────────────────────────────
#  MATCHING
# ──────────────────────────────────────────────
class Matching(db.Model):
    __tablename__ = 'matchings'

    id             = db.Column(db.Integer, primary_key=True)
    mentor_id      = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    mentore_id     = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    score          = db.Column(db.Float,   nullable=False)
    statut         = db.Column(db.String(20), default='en_attente')   # en_attente | accepte | refuse
    date_creation  = db.Column(db.DateTime, default=datetime.utcnow)

    mentor  = db.relationship('Utilisateur', foreign_keys=[mentor_id])
    mentore = db.relationship('Utilisateur', foreign_keys=[mentore_id])


# ──────────────────────────────────────────────
#  CONVERSATION
# ──────────────────────────────────────────────
class Conversation(db.Model):
    __tablename__ = 'conversations'

    id            = db.Column(db.Integer, primary_key=True)
    user1_id      = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    user2_id      = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship('Message', backref='conversation', lazy=True,
                               order_by='Message.date_envoi', cascade='all, delete-orphan')
    user1 = db.relationship('Utilisateur', foreign_keys=[user1_id])
    user2 = db.relationship('Utilisateur', foreign_keys=[user2_id])

    # Garantit unicité : on stocke toujours le plus petit id en user1
    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', name='unique_conversation'),
    )

    def autre_participant(self, user_id):
        """Retourne l'autre participant de la conversation."""
        return self.user2 if self.user1_id == user_id else self.user1


# ──────────────────────────────────────────────
#  MESSAGE
# ──────────────────────────────────────────────
class Message(db.Model):
    __tablename__ = 'messages'

    id              = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'),  nullable=False)
    contenu         = db.Column(db.Text, nullable=False)
    lu              = db.Column(db.Boolean, default=False)
    date_envoi      = db.Column(db.DateTime, default=datetime.utcnow)

    expediteur = db.relationship('Utilisateur', foreign_keys=[user_id])

    def to_dict(self):
        return {
            'id':              self.id,
            'conversation_id': self.conversation_id,
            'user_id':         self.user_id,
            'contenu':         self.contenu,
            'lu':              self.lu,
            'date_envoi':      self.date_envoi.isoformat()
        }
