<div align="center">


# IFRI MentorLink

**La plateforme de mentorat des étudiants de l'IFRI — s'entraider, partager ses compétences et réussir ensemble.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Licence](https://img.shields.io/badge/Licence-Académique-blue)](#-licence--contexte)

</div>

---

##  Table des matières

- [À propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Captures d'écran](#-captures-décran)
- [Stack technique](#️-stack-technique)
- [Structure du projet](#-structure-du-projet)
- [Prérequis](#️-prérequis)
- [Installation & lancement](#-installation--lancement)
- [Configuration](#-configuration)
- [Base de données](#️-base-de-données)
- [Routes & API](#-routes--api)
- [Utilisation](#-utilisation)
- [Équipe](#-équipe)
- [Licence & contexte](#-licence--contexte)

---

##  À propos

**IFRI MentorLink** est une application web de mentorat développée dans le cadre du projet intégrateur (PIL1) à l'**IFRI** (Institut de Formation et de Recherche en Informatique), Université d'Abomey-Calavi.

Elle met en relation les étudiants pour du mentorat académique et professionnel : chacun crée un profil détaillé (filière, niveau, compétences, lacunes, disponibilités), puis un **algorithme de matching** propose automatiquement les binômes mentor / mentoré les plus compatibles, avec un **score de compatibilité**. Les étudiants peuvent ensuite échanger via une **messagerie instantanée**.

L'application couvre les 5 filières de l'IFRI : **IA, IM, GL, SE&IoT, SI** (niveaux L1 à M2).

---

##  Fonctionnalités

-  **Authentification** — inscription, connexion, déconnexion et réinitialisation de mot de passe (Flask-Login, mots de passe hachés).
-  **Profil & compétences** — gestion des informations personnelles, de la filière/niveau, de la bio, des compétences (points forts et lacunes) et des disponibilités horaires.
- **Matching intelligent** — suggestions de binômes basées sur les compétences communes, les disponibilités et la proximité filière/niveau, avec score de compatibilité et filtres par filière.
-  **Messagerie instantanée** — conversations en temps réel, historique conservé et compteur de messages non lus.
-  **Tableau de bord** — vue d'ensemble de l'activité : suggestions, messages non lus, taux de complétion du profil et conversations récentes.
- **Système de design unifié** — thème sombre, dégradé bleu → cyan, polices Sora + Plus Jakarta Sans, icônes Font Awesome et logo SVG.

---


##  Stack technique

| Côté | Technologies |
|------|--------------|
| **Backend** | Python 3.10+, Flask, Flask-Login, SQLAlchemy (Flask-SQLAlchemy), Jinja2, Werkzeug |
| **Base de données** | SQLite (développement) — adaptable à MySQL/PostgreSQL via SQLAlchemy |
| **Frontend** | HTML5, CSS3, JavaScript (vanilla), Font Awesome 6.5.2, Google Fonts (Sora, Plus Jakarta Sans) |
| **Outils** | Git / GitHub, environnement virtuel `venv` |

---

##  Structure du projet

> _Structure indicative — adaptez-la à l'organisation réelle de votre dépôt._

```
PIL1_2526_68/  ·
│
├── run.py                    # point d'entrée
├── app.py                    # factory create_app + blueprints
├── config.py                 # configuration
├── extensions.py             # instances partagées (db, login_manager…)
├── models.py                 # modèles
├── schema.sql                # schéma SQL de la base
├── requirements.txt
├── README.md
│
├── rapport/
│   └── rapport.html
│
├── routes/                   # blueprints (logique des pages)
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── users.py
│   ├── matching.py
│   ├── mentorat.py
│   └── messages.py
│
├── static/
│   ├── assets/               # logos + icônes réseaux (SVG)
│   │   ├── logo.svg
│   │   ├── logo-mark.svg
│   │   ├── logo-lockup.svg
│   │   ├── facebook-svgrepo-com.svg
│   │   ├── github-142-svgrepo-com.svg
│   │   ├── linkedin-color-svgrepo-com.svg
│   │   ├── twitter-154-svgrepo-com.svg
│   │   └── youtube-you-tube-video-svgrepo-com.svg
│   │
│   ├── css/
│   │   ├── auth.css
│   │   ├── login.css
│   │   ├── register.css
│   │   ├── dashboard.css
│   │   ├── profil.css
│   │   ├── matching.css
│   │   ├── mentorat.css
│   │   ├── messages.css
│   │   └── css/               sous-dossier dupliqué
│   │       ├── about.css
│   │       ├── base.css
│   │       ├── contact.css
│   │       ├── footer.css
│   │       ├── header.css
│   │       ├── hero.css
│   │       ├── how-it-works.css
│   │       └── services.css
│   │
│   └── js/
│       ├── matching.js
│       ├── mentorat.js
│       └── messages.js
│
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── reset_password.html
    ├── dashboard.html
    ├── profil.html
    ├── voir_profil.html
    ├── matching.html
    ├── messages.html
    ├── mentorat_offres.html
    ├── mentorat_seances.html
    ├── condit_utili.html
    └── confidentialite.html

---

##  Prérequis

- **Python 3.10+**
- **pip**
- **Git**
- (Optionnel) Un serveur **MySQL/PostgreSQL** si vous n'utilisez pas SQLite

---

##  Installation & lancement

```bash
# 1. Cloner le dépôt
 https://github.com/Kim-AII/PIL1_2526_68.git
cd OIL1_2526_68

# 2. Créer et activer un environnement virt
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement (voir la section Configuration)

# 5. Initialiser la base de données (voir la section Base de données)

# 6. Lancer l'application
python run.py
```

L'application est ensuite accessible sur **http://localhost:5000**.

>  Si vous n'avez pas encore de `requirements.txt`, générez-le avec :
> ```bash
> pip freeze > requirements.txt
> ```
> Contenu minimal attendu :
> ```
> Flask
> Flask-Login
> Flask-SQLAlchemy
> Flask-Migrate        # si vous utilisez les migrations
> Werkzeug
> python-dotenv        # si vous chargez un fichier .env
> ```

---

##  Configuration

La configuration est centralisée dans **`config.py`**. Exemple :

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Clé secrète (sessions, Flask-Login, CSRF…)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-cette-cle-en-production'

    # Base de données SQLite locale (fichier mentorlink.db)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
        or 'sqlite:///' + os.path.join(basedir, 'mentorlink.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Variables d'environnement (optionnelles) :

| Variable | Rôle | Par défaut |
|----------|------|------------|
| `SECRET_KEY` | Clé de sécurité des sessions | valeur de dev |
| `DATABASE_URL` | URL de connexion à la base | SQLite local |

> Pour MySQL : `DATABASE_URL=mysql+pymysql://user:motdepasse@localhost/mentorlink` (nécessite `pip install pymysql`).

---

##  Base de données

Modèles principaux (SQLAlchemy) :

| Modèle | Champs clés | Description |
|--------|-------------|-------------|
| **Utilisateur** | `id`, `nom`, `prenom`, `email`, `telephone`, `mot_de_passe` (haché), `filiere`, `niveau`, `bio`, `photo_url` | Compte étudiant |
| **Compétence** | `id`, `nom` (+ liaison au profil avec un type : *fort* / *lacune*) | Compétences déclarées |
| **Disponibilité** | `id`, `jour`, `heure_debut`, `heure_fin`, `user_id` | Créneaux de disponibilité |
| **Conversation** | `id`, participants | Fil de discussion entre 2 utilisateurs |
| **Message** | `id`, `conversation_id`, `user_id`, `contenu`, `date_envoi`, `lu` | Message échangé |
| **Matching** | utilisateurs concernés, `score` | Compatibilité calculée |

**Initialisation** (à adapter selon votre configuration) :

```bash
# Option A — avec Flask-Migrate
flask db init
flask db migrate -m "Schéma initial"
flask db upgrade

# Option B — création directe via le shell
flask shell
>>> from app import db
>>> db.create_all()
```

---

##  Routes & API

### Pages

| Route | Endpoint | Description |
|-------|----------|-------------|
| `/` | `main.index` | Page d'accueil |
| `/inscription` | `auth.register` | Création de compte |
| `/connexion` | `auth.login` | Connexion |
| `/deconnexion` | `auth.logout` | Déconnexion |
| `/dashboard` | `users.dashboard` | Tableau de bord |
| `/profil` | `users.profil` | Profil & compétences |
| `/matching` | `matching.page_matching` | Suggestions de binômes |
| `/messages` | `messages.page_messages` | Messagerie |

> _Les chemins exacts (`/inscription`, `/connexion`, …) peuvent varier selon vos blueprints ; les noms d'endpoints, eux, sont ceux utilisés dans les `url_for(...)`._

### API (JSON)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/utilisateur/<id>` | Profil public d'un utilisateur |
| `GET` | `/api/messages/conversation/<id>` | Conversation et messages avec un utilisateur |
| `GET` | `/api/messages/non-lus` | Nombre de messages non lus |
| `GET` | `/api/competences` | Liste des compétences disponibles |
| `POST` | `/api/profil/competences` | Ajouter / retirer une compétence |
| `POST` | `/api/profil/disponibilites` | Ajouter / retirer une disponibilité |

---

##  Utilisation

1. **Créer un compte** depuis la page d'inscription (nom, prénom, email, filière, niveau…).
2. **Compléter son profil** : ajouter ses compétences (points forts / lacunes) et ses disponibilités — un profil complet améliore la qualité des suggestions.
3. **Consulter le matching** : parcourir les binômes suggérés, filtrer par filière, consulter une fiche profil.
4. **Contacter** un mentor / mentoré : ouvrir la messagerie et démarrer une conversation.
5. **Suivre son activité** depuis le tableau de bord.

---

##  Équipe

Projet réalisé par le groupe 68, IFRI — UAC (PIL1 2025/2026) :

| Membre | Rôle |
|--------|------|
| **GNAGO Béga Modeste** | Chef de groupe — Authentification, connexion & inscription |
| **ADANDE Idelphonse Aziz** | Matching (en tandem avec Regina) |
| **Regina MONTCHO** | Matching (en tandem avec Aziz) |
| **ABOUDOU KARIM YOUSSAO Nourou Dine** | Messagerie (en tandem avec Sandrine) |
| **KESSOU Sandrine** | Messagerie (en tandem avec Dine) |
| **KARIM ISSAOU Abdou-Hakim** | Tests, gestion du dépôt, tableau de bord & profil |
| **KOKOBITA Exaucée Martinienne OLUWA-TOSSIN** | Rédaction du rapport & documentation |

---

##  Licence & contexte

Projet académique développé dans le cadre du **projet intégrateur (PIL1)** à l'**IFRI — Université d'Abomey-Calavi**, Bénin.
Usage pédagogique. Tous droits réservés à l'équipe de développement.

---

<div align="center">

Fait par l'équipe 68  IFRI MentorLink — UAC · IFRI

</div>
