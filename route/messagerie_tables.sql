-- ================================================================
-- IFRI MentorLink - Tables Messagerie
-- A ajouter dans mentorlink_db
-- ================================================================

USE mentorlink_db;

-- Table des conversations
CREATE TABLE IF NOT EXISTS conversations (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user1_id      INT NOT NULL,
    user2_id      INT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (user2_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_conv (user1_id, user2_id)
);

-- Table des messages
CREATE TABLE IF NOT EXISTS messages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    user_id         INT NOT NULL,
    contenu         TEXT NOT NULL,
    date_envoi      DATETIME DEFAULT CURRENT_TIMESTAMP,
    lu              TINYINT(1) DEFAULT 0,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conv ON messages(conversation_id);
CREATE INDEX idx_messages_user ON messages(user_id);
