from app import create_app
from extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # Crée les tables si elles n'existent pas
        print("✅ Tables créées.")
    app.run(debug=True, host='0.0.0.0', port=5000)
