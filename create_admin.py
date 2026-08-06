from werkzeug.security import generate_password_hash


def seed_admin():
    from extensions import db
    from models import User

    existing = User.query.filter_by(role='admin').first()
    if existing:
        return

    admin = User(
        username='admin',
        email='admin@trek.com',
        password_hash=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin created: admin / admin123')
