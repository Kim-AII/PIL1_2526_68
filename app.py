from flask import Flask
from extensions import db, login_manager, bcrypt
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Configuration de Flask-Login
    login_manager.login_view    = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'warning'

    # Enregistrement des blueprints
    from routes.main     import main_bp
    from routes.auth     import auth_bp
    from routes.users    import users_bp
    from routes.matching import matching_bp
    from routes.messages import messages_bp
    from routes.mentorat import mentorat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(mentorat_bp)

    return app
