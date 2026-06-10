-- ============================================================
--  IFRI_MentorLink — schema.sql
--  Base de données : mentorlink_db
--  Encodage : utf8mb4
-- ============================================================

DROP DATABASE IF EXISTS mentorlink_db;

CREATE DATABASE mentorlink_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mentorlink_db;

-- ──────────────────────────────────────────────
--  UTILISATEURS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS utilisateurs (
    id               INT          AUTO_INCREMENT PRIMARY KEY,
    nom              VARCHAR(100) NOT NULL,
    prenom           VARCHAR(100) NOT NULL,
    email            VARCHAR(150) NOT NULL UNIQUE,
    telephone        VARCHAR(20)  NOT NULL UNIQUE,
    mot_de_passe     VARCHAR(255) NOT NULL,
    filiere          ENUM('IA', 'IM', 'GL', 'SE_IoT', 'SI') DEFAULT NULL,
    niveau           ENUM('L1', 'L2', 'L3', 'M1', 'M2')    DEFAULT NULL,
    bio              TEXT,
    photo_url        VARCHAR(255),
    date_inscription DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  COMPÉTENCES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS competences (
    id        INT          AUTO_INCREMENT PRIMARY KEY,
    nom       VARCHAR(100) NOT NULL UNIQUE,
    categorie VARCHAR(50)
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  USER_COMPETENCES  (jonction utilisateur ↔ compétence)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_competences (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    competence_id INT NOT NULL,
    type          ENUM('fort', 'faible') NOT NULL,
    FOREIGN KEY (user_id)       REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competences(id)  ON DELETE CASCADE,
    UNIQUE KEY unique_user_competence (user_id, competence_id)
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  DISPONIBILITÉS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS disponibilites (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    jour        ENUM('Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche') NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin   TIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  MATCHINGS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS matchings (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    mentor_id     INT          NOT NULL,
    mentore_id    INT          NOT NULL,
    score         FLOAT        NOT NULL,
    statut        ENUM('en_attente', 'accepte', 'refuse') DEFAULT 'en_attente',
    date_creation DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id)  REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (mentore_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  CONVERSATIONS
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id            INT      AUTO_INCREMENT PRIMARY KEY,
    user1_id      INT      NOT NULL,   -- toujours le plus petit id
    user2_id      INT      NOT NULL,   -- toujours le plus grand id
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (user2_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_conversation (user1_id, user2_id)
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  MESSAGES
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id              INT      AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT      NOT NULL,
    user_id         INT      NOT NULL,
    contenu         TEXT     NOT NULL,
    lu              BOOLEAN  DEFAULT FALSE,
    date_envoi      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)         REFERENCES utilisateurs(id)  ON DELETE CASCADE,
    INDEX idx_conversation (conversation_id),
    INDEX idx_non_lus      (lu, user_id)
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  OFFRES MENTORAT
--  type_publication : 'offre' (mentor propose) | 'demande' (mentoré cherche)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS offres_mentorat (
    id               INT          AUTO_INCREMENT PRIMARY KEY,
    auteur_id        INT          NOT NULL,
    type_publication ENUM('offre','demande') NOT NULL,
    titre            VARCHAR(150) NOT NULL,
    description      TEXT,
    competence_id    INT          DEFAULT NULL,
    niveau_cible     ENUM('L1','L2','L3','M1','M2') DEFAULT NULL,
    filiere_cible    ENUM('IA','IM','GL','SE_IoT','SI') DEFAULT NULL,
    max_places       INT          DEFAULT 1,
    statut           ENUM('ouverte','fermee','archivee') DEFAULT 'ouverte',
    date_creation    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auteur_id)     REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competences(id)  ON DELETE SET NULL,
    INDEX idx_offres_statut (statut),
    INDEX idx_offres_type   (type_publication)
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  CANDIDATURES OFFRES
--  Réponse d'un utilisateur à une offre ou demande
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS candidatures_offres (
    id               INT      AUTO_INCREMENT PRIMARY KEY,
    offre_id         INT      NOT NULL,
    candidat_id      INT      NOT NULL,
    message          TEXT,
    statut           ENUM('en_attente','acceptee','refusee') DEFAULT 'en_attente',
    date_candidature DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (offre_id)    REFERENCES offres_mentorat(id) ON DELETE CASCADE,
    FOREIGN KEY (candidat_id) REFERENCES utilisateurs(id)    ON DELETE CASCADE,
    UNIQUE KEY unique_candidature (offre_id, candidat_id)
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  SEANCES MENTORAT
--  Créée automatiquement quand une candidature est acceptée
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS seances_mentorat (
    id             INT          AUTO_INCREMENT PRIMARY KEY,
    offre_id       INT          NOT NULL,
    candidature_id INT          NOT NULL,
    mentor_id      INT          NOT NULL,
    mentore_id     INT          NOT NULL,
    date_seance    DATETIME     DEFAULT NULL,
    duree_minutes  INT          DEFAULT 60,
    lieu           VARCHAR(255),
    statut         ENUM('planifiee','confirmee','terminee','annulee') DEFAULT 'planifiee',
    notes          TEXT,
    date_creation  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (offre_id)       REFERENCES offres_mentorat(id)    ON DELETE CASCADE,
    FOREIGN KEY (candidature_id) REFERENCES candidatures_offres(id) ON DELETE CASCADE,
    FOREIGN KEY (mentor_id)      REFERENCES utilisateurs(id)        ON DELETE CASCADE,
    FOREIGN KEY (mentore_id)     REFERENCES utilisateurs(id)        ON DELETE CASCADE,
    INDEX idx_seances_mentor  (mentor_id),
    INDEX idx_seances_mentore (mentore_id),
    INDEX idx_seances_statut  (statut)
) ENGINE=InnoDB;

-- ──────────────────────────────────────────────
--  DONNÉES INITIALES : compétences par défaut
-- ──────────────────────────────────────────────
INSERT IGNORE INTO competences (nom, categorie) VALUES
    ('programation Python',                                           'Programmation'),
    ('développement web',                                             'Programmation'),
    ('Infographie',                                                   'Programmation'),
    ('SGBD et language SQL',                                        'Base de données'),
    ('Bases de données et algèbres relationnnelles',                'Base de données'),
    ('Recherche opérationnelle',                                       'Informatique'),
    ('Théorie des graphes',                                            'Informatique'),
    ('Projet intégrateur',                                             'Informatique'),
    ('Architecture et topologie des réseaux',                              'Systèmes'),
    ('Utilisation et administration sous windows et linux',                'Systèmes'),
    ('Outils de base en informatique',                                 'informatique'),
    ('Algorithmes',                                                        'Systèmes'),
    ('language C',                                                         'Systèmes'),
    ('Administration des réseaux sous windows et linux',                   'Systèmes'),
    ('probabilités',                                   ' mathématiques fondamentales'),
    ('Statistique inférentielles',                      'mathématiques fondamentales'),
    ('Analyse et application',                          'Mathématiques fondamentales'),
    ('Algèbre linéaire',                                'mathématiques fondamentales'),
    ('logiques arithmétiques',                          'mathématiques fondamentales'),
    ('équations différentielles',                       'mathématiques fondamentales'),
    ('Suite et séries numeriques',                      'Mathématiques fondamentales'),
    ('Anglais technique',                                          'culture générale'),
    ('Déontologie',                                                'culture générale'),
    ('TEEO',                                                       'culture générale');


