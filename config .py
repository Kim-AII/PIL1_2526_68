
import os

class Config:
    # Clé secrète pour les sessions — à changer en production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mentorlink-ifri-secret-2026')

    # Connexion MySQL — modifier selon votre environnement
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/mentorlink_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Taille max d'upload (photos de profil)
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 Mo
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/mentorlink_db'