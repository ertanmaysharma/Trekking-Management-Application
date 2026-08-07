from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_, func
from functools import wraps
from datetime import datetime
import json

from extensions import db
from models import User, Trek, Booking, StaffProfile

main = Blueprint('main', __name__)


# ── role decorators ──────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated


def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'staff':
            flash('Staff access required.', 'danger')
            return redirect(url_for('main.login'))
        if not current_user.staff_profile or not current_user.staff_profile.is_approved:
            flash('Your account is pending admin approval.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'user':
            flash('User access required.', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated


# ── index ────────────────────────────────────────────────────────────────────

@main.route('/')
def index():
    return redirect(url_for('main.login'))


# ── auth ─────────────────────────────────────────────────────────────────────

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        role     = request.form.get('role', 'user')
        contact  = request.form.get('contact', '').strip()

        # backend validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.register'))

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return redirect(url_for('main.register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('main.register'))

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('main.register'))

        if role not in ('user', 'staff'):
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('main.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('main.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.flush()

        if role == 'staff':
            profile = StaffProfile(user_id=user.id, contact=contact)
            db.session.add(profile)

        db.session.commit()

        if role == 'staff':
            flash('Staff account created. Waiting for admin approval.', 'info')
        else:
            flash('Account created successfully. Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('auth/register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('main.login'))

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('main.login'))

        if user.is_blacklisted:
            flash('Your account has been blacklisted. Contact admin.', 'danger')
            return redirect(url_for('main.login'))

        if user.role == 'staff':
            if not user.staff_profile or not user.staff_profile.is_approved:
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('main.login'))

        login_user(user)

        if user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif user.role == 'staff':
            return redirect(url_for('main.staff_dashboard'))
        else:
            return redirect(url_for('main.user_dashboard'))

    return render_template('auth/login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# ── admin ─────────────────────────────────────────────────────────────────────

@main.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_treks    = Trek.query.count()
    total_users    = User.query.filter_by(role='user').count()
    total_staff    = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    pending_staff  = StaffProfile.query.filter_by(is_approved=False).count()

    # chart data: trek status distribution
    trek_status_rows = db.session.query(Trek.status, func.count(Trek.id)).group_by(Trek.status).all()
    trek_status_data = {s: c for s, c in trek_status_rows}

    # chart data: booking status distribution
    booking_status_rows = db.session.query(Booking.status, func.count(Booking.id)).group_by(Booking.status).all()
    booking_status_data = {s: c for s, c in booking_status_rows}

    # chart data: top 5 treks by booking count
    top_treks = db.session.query(Trek.name, func.count(Booking.id).label('cnt'))\
        .join(Booking, Trek.id == Booking.trek_id, isouter=True)\
        .group_by(Trek.id).order_by(func.count(Booking.id).desc()).limit(5).all()
    top_trek_labels = [row[0] for row in top_treks]
    top_trek_counts = [row[1] for row in top_treks]

    return render_template('admin/dashboard.html',
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings,
        pending_staff=pending_staff,
        trek_status_json=json.dumps(trek_status_data),
        booking_status_json=json.dumps(booking_status_data),
        top_trek_labels=json.dumps(top_trek_labels),
        top_trek_counts=json.dumps(top_trek_counts),
    )


@main.route('/admin/treks')
@admin_required
def admin_treks():
    approved_staff = User.query.filter_by(role='staff').join(StaffProfile).filter(StaffProfile.is_approved == True).all()
    treks = Trek.query.order_by(Trek.created_at.desc()).all()
    return render_template('admin/treks.html', treks=treks, staff_list=approved_staff)


@main.route('/admin/treks/create', methods=['GET', 'POST'])
@admin_required
def admin_create_trek():
    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        location    = request.form.get('location', '').strip()
        difficulty  = request.form.get('difficulty')
        duration    = request.form.get('duration')
        total_slots = request.form.get('total_slots')
        status      = request.form.get('status', 'Pending')
        start_date  = request.form.get('start_date')
        end_date    = request.form.get('end_date')
        description = request.form.get('description', '').strip()

        # backend validation
        errors = []
        if not name:
            errors.append('Trek name is required.')
        if not location:
            errors.append('Location is required.')
        if difficulty not in ('Easy', 'Moderate', 'Hard'):
            errors.append('Invalid difficulty.')
        if not duration or int(duration) < 1:
            errors.append('Duration must be at least 1 day.')
        if not total_slots or int(total_slots) < 1:
            errors.append('Total slots must be at least 1.')
        if start_date and end_date and start_date > end_date:
            errors.append('End date must be after start date.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return redirect(url_for('main.admin_create_trek'))

        slots = int(total_slots)
        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=int(duration),
            total_slots=slots,
            available_slots=slots,
            status=status,
            description=description,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        )
        db.session.add(trek)
        db.session.commit()
        flash('Trek created successfully.', 'success')
        return redirect(url_for('main.admin_treks'))

    return render_template('admin/trek_form.html', trek=None)


@main.route('/admin/treks/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_trek(id):
    trek = db.get_or_404(Trek, id)
    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        location    = request.form.get('location', '').strip()
        difficulty  = request.form.get('difficulty')
        duration    = request.form.get('duration')
        total_slots = request.form.get('total_slots')
        start_date  = request.form.get('start_date')
        end_date    = request.form.get('end_date')

        if not name or not location:
            flash('Name and location are required.', 'danger')
            return redirect(url_for('main.admin_edit_trek', id=id))
        if start_date and end_date and start_date > end_date:
            flash('End date must be after start date.', 'danger')
            return redirect(url_for('main.admin_edit_trek', id=id))

        trek.name        = name
        trek.location    = location
        trek.difficulty  = difficulty
        trek.duration    = int(duration)
        trek.total_slots = int(total_slots)
        trek.status      = request.form.get('status', trek.status)
        trek.description = request.form.get('description', '').strip()
        trek.start_date  = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        trek.end_date    = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        db.session.commit()
        flash('Trek updated.', 'success')
        return redirect(url_for('main.admin_treks'))
    return render_template('admin/trek_form.html', trek=trek)


@main.route('/admin/treks/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_trek(id):
    trek = db.get_or_404(Trek, id)
    Booking.query.filter_by(trek_id=id).delete()
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted.', 'success')
    return redirect(url_for('main.admin_treks'))


@main.route('/admin/treks/<int:id>/assign', methods=['POST'])
@admin_required
def admin_assign_staff(id):
    trek = db.get_or_404(Trek, id)
    staff_id = request.form.get('staff_id')
    trek.assigned_staff_id = int(staff_id) if staff_id else None
    db.session.commit()
    flash('Staff assignment updated.', 'success')
    return redirect(url_for('main.admin_treks'))


@main.route('/admin/users')
@admin_required
def admin_users():
    q = request.args.get('q', '').strip()
    query = User.query.filter_by(role='user')
    if q:
        query = query.filter(or_(User.username.ilike(f'%{q}%'), User.email.ilike(f'%{q}%')))
    users = query.all()
    return render_template('admin/users.html', users=users, q=q)


@main.route('/admin/users/<int:id>/blacklist', methods=['POST'])
@admin_required
def admin_blacklist_user(id):
    user = db.get_or_404(User, id)
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    msg = 'blacklisted' if user.is_blacklisted else 'unblacklisted'
    flash(f'User {user.username} {msg}.', 'success')
    return redirect(url_for('main.admin_users'))


@main.route('/admin/staff')
@admin_required
def admin_staff():
    q = request.args.get('q', '').strip()
    query = User.query.filter_by(role='staff')
    if q:
        query = query.filter(or_(User.username.ilike(f'%{q}%'), User.email.ilike(f'%{q}%')))
    staff_users = query.all()
    return render_template('admin/staff.html', staff_users=staff_users, q=q)


@main.route('/admin/staff/<int:id>/approve', methods=['POST'])
@admin_required
def admin_approve_staff(id):
    user = db.get_or_404(User, id)
    if user.staff_profile:
        user.staff_profile.is_approved = True
        db.session.commit()
        flash(f'{user.username} approved.', 'success')
    return redirect(url_for('main.admin_staff'))


@main.route('/admin/staff/<int:id>/blacklist', methods=['POST'])
@admin_required
def admin_blacklist_staff(id):
    user = db.get_or_404(User, id)
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    msg = 'blacklisted' if user.is_blacklisted else 'unblacklisted'
    flash(f'Staff {user.username} {msg}.', 'success')
    return redirect(url_for('main.admin_staff'))


@main.route('/admin/bookings')
@admin_required
def admin_bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)


@main.route('/admin/search')
@admin_required
def admin_search():
    q        = request.args.get('q', '').strip()
    category = request.args.get('category', 'treks')
    results  = []

    if q:
        if category == 'treks':
            results = Trek.query.filter(
                or_(Trek.name.ilike(f'%{q}%'), Trek.location.ilike(f'%{q}%'))
            ).all()
        elif category == 'users':
            results = User.query.filter(
                User.role == 'user',
                or_(User.username.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'))
            ).all()
        elif category == 'staff':
            results = User.query.filter(
                User.role == 'staff',
                or_(User.username.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'))
            ).all()

    return render_template('admin/search.html', results=results, q=q, category=category)


# ── staff ─────────────────────────────────────────────────────────────────────

@main.route('/staff/dashboard')
@staff_required
def staff_dashboard():
    treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()

    # chart: participants per trek
    chart_labels = [t.name for t in treks]
    chart_data   = [
        Booking.query.filter_by(trek_id=t.id, status='Booked').count()
        for t in treks
    ]

    return render_template('staff/dashboard.html',
        treks=treks,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
    )


@main.route('/staff/treks/<int:id>', methods=['GET', 'POST'])
@staff_required
def staff_trek_detail(id):
    trek = db.get_or_404(Trek, id)

    if trek.assigned_staff_id != current_user.id:
        flash('You are not assigned to this trek.', 'danger')
        return redirect(url_for('main.staff_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_slots':
            val = request.form.get('available_slots')
            if val is not None:
                new_slots = int(val)
                if new_slots < 0:
                    flash('Slots cannot be negative.', 'danger')
                    return redirect(url_for('main.staff_trek_detail', id=id))
                if new_slots > trek.total_slots:
                    flash(f'Slots cannot exceed total slots ({trek.total_slots}).', 'danger')
                    return redirect(url_for('main.staff_trek_detail', id=id))
                trek.available_slots = new_slots

        elif action == 'update_status':
            new_status = request.form.get('status')
            if new_status not in ('Open', 'Closed', 'Completed'):
                flash('Invalid status.', 'danger')
                return redirect(url_for('main.staff_trek_detail', id=id))
            trek.status = new_status
            if new_status == 'Completed':
                for b in trek.bookings:
                    if b.status == 'Booked':
                        b.status = 'Completed'

        db.session.commit()
        flash('Trek updated.', 'success')
        return redirect(url_for('main.staff_trek_detail', id=id))

    participants = Booking.query.filter_by(trek_id=id).filter(Booking.status != 'Cancelled').all()
    return render_template('staff/trek_detail.html', trek=trek, participants=participants)


# ── user ─────────────────────────────────────────────────────────────────────

@main.route('/user/dashboard')
@user_required
def user_dashboard():
    my_bookings = Booking.query.filter_by(user_id=current_user.id)\
        .order_by(Booking.booking_date.desc()).limit(5).all()
    open_treks  = Trek.query.filter_by(status='Open').limit(6).all()

    # chart: my booking status distribution
    booking_rows = db.session.query(Booking.status, func.count(Booking.id))\
        .filter_by(user_id=current_user.id).group_by(Booking.status).all()
    booking_chart = {s: c for s, c in booking_rows}

    return render_template('user/dashboard.html',
        my_bookings=my_bookings,
        open_treks=open_treks,
        booking_chart_json=json.dumps(booking_chart),
    )


@main.route('/user/treks')
@user_required
def user_treks():
    q          = request.args.get('q', '').strip()
    location   = request.args.get('location', '').strip()
    difficulty = request.args.get('difficulty', '').strip()

    query = Trek.query.filter_by(status='Open')
    if q:
        query = query.filter(Trek.name.ilike(f'%{q}%'))
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    treks = query.all()
    return render_template('user/treks.html', treks=treks, q=q, location=location, difficulty=difficulty)


@main.route('/user/treks/<int:id>/book', methods=['POST'])
@user_required
def user_book_trek(id):
    trek = db.get_or_404(Trek, id)

    if trek.status != 'Open':
        flash('This trek is not open for booking.', 'danger')
        return redirect(url_for('main.user_treks'))

    if trek.available_slots <= 0:
        flash('No available slots for this trek.', 'danger')
        return redirect(url_for('main.user_treks'))

    already = Booking.query.filter_by(
        user_id=current_user.id, trek_id=id, status='Booked'
    ).first()
    if already:
        flash('You have already booked this trek.', 'warning')
        return redirect(url_for('main.user_treks'))

    booking = Booking(user_id=current_user.id, trek_id=id)
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()

    flash(f'"{trek.name}" booked successfully!', 'success')
    return redirect(url_for('main.user_bookings'))


@main.route('/user/bookings')
@user_required
def user_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id)\
        .order_by(Booking.booking_date.desc()).all()
    return render_template('user/bookings.html', bookings=bookings)


@main.route('/user/bookings/<int:id>/cancel', methods=['POST'])
@user_required
def user_cancel_booking(id):
    booking = db.get_or_404(Booking, id)

    if booking.user_id != current_user.id:
        flash('Not your booking.', 'danger')
        return redirect(url_for('main.user_bookings'))

    if booking.status != 'Booked':
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('main.user_bookings'))

    booking.status = 'Cancelled'
    booking.trek.available_slots += 1
    db.session.commit()
    flash('Booking cancelled.', 'info')
    return redirect(url_for('main.user_bookings'))


@main.route('/user/profile', methods=['GET', 'POST'])
@user_required
def user_profile():
    if request.method == 'POST':
        new_email    = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()

        if not new_email:
            flash('Email cannot be empty.', 'danger')
            return redirect(url_for('main.user_profile'))

        if new_email != current_user.email:
            taken = User.query.filter_by(email=new_email).first()
            if taken:
                flash('Email already in use.', 'danger')
                return redirect(url_for('main.user_profile'))
            current_user.email = new_email

        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return redirect(url_for('main.user_profile'))
            current_user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('main.user_profile'))

    return render_template('user/profile.html', user=current_user)
