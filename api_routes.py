from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from extensions import db
from models import Trek, Booking, User, StaffProfile
from datetime import datetime

api = Blueprint('api', __name__)


def admin_only():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return None


# ── Treks API ──────────────────────────────────────────────────────────────

@api.route('/treks', methods=['GET'])
def get_treks():
    status = request.args.get('status')
    difficulty = request.args.get('difficulty')
    location = request.args.get('location')

    query = Trek.query
    if status:
        query = query.filter_by(status=status)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))

    treks = query.all()
    return jsonify([t.to_dict() for t in treks])


@api.route('/treks/<int:id>', methods=['GET'])
def get_trek(id):
    trek = db.get_or_404(Trek, id)
    data = trek.to_dict()
    data['booking_count'] = Booking.query.filter_by(trek_id=id, status='Booked').count()
    return jsonify(data)


@api.route('/treks', methods=['POST'])
@login_required
def create_trek():
    err = admin_only()
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['name', 'location', 'difficulty', 'duration', 'total_slots']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if data['difficulty'] not in ('Easy', 'Moderate', 'Hard'):
        return jsonify({'error': 'difficulty must be Easy, Moderate, or Hard'}), 400

    slots = int(data['total_slots'])
    trek = Trek(
        name=data['name'].strip(),
        location=data['location'].strip(),
        difficulty=data['difficulty'],
        duration=int(data['duration']),
        total_slots=slots,
        available_slots=slots,
        status=data.get('status', 'Pending'),
        description=data.get('description', ''),
    )
    db.session.add(trek)
    db.session.commit()
    return jsonify(trek.to_dict()), 201


@api.route('/treks/<int:id>', methods=['PUT'])
@login_required
def update_trek(id):
    err = admin_only()
    if err:
        return err

    trek = db.get_or_404(Trek, id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        trek.name = data['name'].strip()
    if 'location' in data:
        trek.location = data['location'].strip()
    if 'difficulty' in data:
        if data['difficulty'] not in ('Easy', 'Moderate', 'Hard'):
            return jsonify({'error': 'Invalid difficulty'}), 400
        trek.difficulty = data['difficulty']
    if 'duration' in data:
        trek.duration = int(data['duration'])
    if 'total_slots' in data:
        trek.total_slots = int(data['total_slots'])
    if 'available_slots' in data:
        trek.available_slots = int(data['available_slots'])
    if 'status' in data:
        if data['status'] not in ('Pending', 'Open', 'Closed', 'Completed'):
            return jsonify({'error': 'Invalid status'}), 400
        trek.status = data['status']
    if 'description' in data:
        trek.description = data['description']

    db.session.commit()
    return jsonify(trek.to_dict())


@api.route('/treks/<int:id>', methods=['DELETE'])
@login_required
def delete_trek(id):
    err = admin_only()
    if err:
        return err

    trek = db.get_or_404(Trek, id)
    Booking.query.filter_by(trek_id=id).delete()
    db.session.delete(trek)
    db.session.commit()
    return jsonify({'message': f'Trek {id} deleted'})


# ── Users API ──────────────────────────────────────────────────────────────

@api.route('/users', methods=['GET'])
@login_required
def get_users():
    err = admin_only()
    if err:
        return err

    role = request.args.get('role')
    query = User.query
    if role:
        query = query.filter_by(role=role)
    users = query.all()
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'is_blacklisted': u.is_blacklisted,
            'created_at': u.created_at.isoformat(),
        })
    return jsonify(result)


@api.route('/users/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    err = admin_only()
    if err:
        return err

    u = db.get_or_404(User, id)
    return jsonify({
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'is_blacklisted': u.is_blacklisted,
        'created_at': u.created_at.isoformat(),
        'booking_count': len(u.bookings),
    })


# ── Bookings API ───────────────────────────────────────────────────────────

@api.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    if current_user.role == 'admin':
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    elif current_user.role == 'user':
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
    else:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify([b.to_dict() for b in bookings])


@api.route('/bookings', methods=['POST'])
@login_required
def create_booking():
    if current_user.role != 'user':
        return jsonify({'error': 'Only users can book treks'}), 403

    data = request.get_json()
    if not data or not data.get('trek_id'):
        return jsonify({'error': 'trek_id is required'}), 400

    trek = db.session.get(Trek, data['trek_id'])
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.status != 'Open':
        return jsonify({'error': 'Trek is not open for booking'}), 400

    if trek.available_slots <= 0:
        return jsonify({'error': 'No slots available'}), 400

    already = Booking.query.filter_by(
        user_id=current_user.id, trek_id=trek.id, status='Booked'
    ).first()
    if already:
        return jsonify({'error': 'You have already booked this trek'}), 400

    booking = Booking(user_id=current_user.id, trek_id=trek.id)
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking.to_dict()), 201


@api.route('/bookings/<int:id>', methods=['GET'])
@login_required
def get_booking(id):
    booking = db.get_or_404(Booking, id)
    if current_user.role != 'admin' and booking.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    return jsonify(booking.to_dict())


@api.route('/bookings/<int:id>', methods=['DELETE'])
@login_required
def cancel_booking(id):
    booking = db.get_or_404(Booking, id)
    if current_user.role != 'admin' and booking.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    if booking.status != 'Booked':
        return jsonify({'error': 'Booking cannot be cancelled'}), 400

    booking.status = 'Cancelled'
    booking.trek.available_slots += 1
    db.session.commit()
    return jsonify({'message': f'Booking {id} cancelled'})


# ── Stats API (admin) ──────────────────────────────────────────────────────

@api.route('/stats', methods=['GET'])
@login_required
def get_stats():
    err = admin_only()
    if err:
        return err

    from sqlalchemy import func
    trek_status = db.session.query(Trek.status, func.count(Trek.id)).group_by(Trek.status).all()
    booking_status = db.session.query(Booking.status, func.count(Booking.id)).group_by(Booking.status).all()

    return jsonify({
        'treks_by_status': {s: c for s, c in trek_status},
        'bookings_by_status': {s: c for s, c in booking_status},
        'total_users': User.query.filter_by(role='user').count(),
        'total_staff': User.query.filter_by(role='staff').count(),
        'total_treks': Trek.query.count(),
        'total_bookings': Booking.query.count(),
    })
