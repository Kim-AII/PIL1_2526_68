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


# ──────────────────────────────────────────────
#  OFFRE MENTORAT
#  type_publication : 'offre' (mentor propose) | 'demande' (mentoré cherche)
# ──────────────────────────────────────────────
class OffreMentorat(db.Model):
    __tablename__ = 'offres_mentorat'

    id               = db.Column(db.Integer, primary_key=True)
    auteur_id        = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    type_publication = db.Column(db.String(10), nullable=False)   # 'offre' | 'demande'
    titre            = db.Column(db.String(150), nullable=False)
    description      = db.Column(db.Text)
    competence_id    = db.Column(db.Integer, db.ForeignKey('competences.id'), nullable=True)
    niveau_cible     = db.Column(db.String(5))     # L1, L2, L3, M1, M2
    filiere_cible    = db.Column(db.String(20))    # IA, IM, GL, SE_IoT, SI
    max_places       = db.Column(db.Integer, default=1)
    statut           = db.Column(db.String(15), default='ouverte')  # ouverte | fermee | archivee
    date_creation    = db.Column(db.DateTime, default=datetime.utcnow)

    auteur       = db.relationship('Utilisateur', foreign_keys=[auteur_id])
    competence   = db.relationship('Competence')
    candidatures = db.relationship('CandidatureOffre', backref='offre', lazy=True,
                                   cascade='all, delete-orphan')

    @property
    def nb_acceptees(self):
        return sum(1 for c in self.candidatures if c.statut == 'acceptee')

    @property
    def places_restantes(self):
        return max(0, self.max_places - self.nb_acceptees)

    def to_dict(self):
        return {
            'id':               self.id,
            'auteur_id':        self.auteur_id,
            'auteur':           self.auteur.to_dict(),
            'type_publication': self.type_publication,
            'titre':            self.titre,
            'description':      self.description,
            'competence':       self.competence.to_dict() if self.competence else None,
            'niveau_cible':     self.niveau_cible,
            'filiere_cible':    self.filiere_cible,
            'max_places':       self.max_places,
            'places_restantes': self.places_restantes,
            'statut':           self.statut,
            'date_creation':    self.date_creation.isoformat()
        }


# ──────────────────────────────────────────────
#  CANDIDATURE OFFRE
#  Réponse d'un utilisateur à une offre ou demande
# ──────────────────────────────────────────────
class CandidatureOffre(db.Model):
    __tablename__ = 'candidatures_offres'

    id               = db.Column(db.Integer, primary_key=True)
    offre_id         = db.Column(db.Integer, db.ForeignKey('offres_mentorat.id'), nullable=False)
    candidat_id      = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'),   nullable=False)
    message          = db.Column(db.Text)
    statut           = db.Column(db.String(15), default='en_attente')  # en_attente | acceptee | refusee
    date_candidature = db.Column(db.DateTime, default=datetime.utcnow)

    candidat = db.relationship('Utilisateur', foreign_keys=[candidat_id])
    seance   = db.relationship('SeanceMentorat', backref='candidature', uselist=False)

    __table_args__ = (
        db.UniqueConstraint('offre_id', 'candidat_id', name='unique_candidature'),
    )

    def to_dict(self):
        return {
            'id':               self.id,
            'offre_id':         self.offre_id,
            'candidat':         self.candidat.to_dict(),
            'message':          self.message,
            'statut':           self.statut,
            'date_candidature': self.date_candidature.isoformat()
        }


# ──────────────────────────────────────────────
#  SEANCE MENTORAT
#  Créée automatiquement quand une candidature est acceptée
# ──────────────────────────────────────────────
class SeanceMentorat(db.Model):
    __tablename__ = 'seances_mentorat'

    id               = db.Column(db.Integer, primary_key=True)
    offre_id         = db.Column(db.Integer, db.ForeignKey('offres_mentorat.id'),  nullable=False)
    candidature_id   = db.Column(db.Integer, db.ForeignKey('candidatures_offres.id'), nullable=False)
    mentor_id        = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'),     nullable=False)
    mentore_id       = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'),     nullable=False)
    date_seance      = db.Column(db.DateTime, nullable=True)
    duree_minutes    = db.Column(db.Integer, default=60)
    lieu             = db.Column(db.String(255))
    statut           = db.Column(db.String(15), default='planifiee')  # planifiee | confirmee | terminee | annulee
    notes            = db.Column(db.Text)
    date_creation    = db.Column(db.DateTime, default=datetime.utcnow)

    offre   = db.relationship('OffreMentorat',  foreign_keys=[offre_id])
    mentor  = db.relationship('Utilisateur',    foreign_keys=[mentor_id])
    mentore = db.relationship('Utilisateur',    foreign_keys=[mentore_id])

    def to_dict(self):
        return {
            'id':            self.id,
            'offre_id':      self.offre_id,
            'offre_titre':   self.offre.titre if self.offre else None,
            'mentor':        self.mentor.to_dict(),
            'mentore':       self.mentore.to_dict(),
            'date_seance':   self.date_seance.isoformat() if self.date_seance else None,
            'duree_minutes': self.duree_minutes,
            'lieu':          self.lieu,
            'statut':        self.statut,
            'notes':         self.notes,
            'date_creation': self.date_creation.isoformat()
        }
