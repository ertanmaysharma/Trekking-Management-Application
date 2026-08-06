from flask import Flask
from config import Config
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        import models  # make sure tables are registered
        db.create_all()

        from create_admin import seed_admin
        seed_admin()

    from routes import main
    app.register_blueprint(main)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
