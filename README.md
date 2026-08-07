# 🥾 Trek Management System

A web-based Trek Management System built with **Flask and SQLite** to make trek planning and booking easier to manage from one place.

The idea behind this project was to build something that feels like a small real-world trek management platform rather than just a basic CRUD application. Different people interact with the system in different ways: an **admin** manages the platform, **staff members** handle the treks assigned to them, and **users** can explore and book available treks.

The project also includes a REST API for working with trek, user, booking, and dashboard data.

---

## 📌 Project Overview

Managing trekking activities manually can become difficult when there are multiple treks, users, staff members, and bookings involved. It is easy to lose track of available slots, staff assignments, booking status, and user information.

This application brings these tasks together into one system.

The application supports three main roles:

- **Admin** – manages users, staff, treks, bookings, and overall platform statistics.
- **Staff** – manages the treks assigned to them and keeps their status and available slots updated.
- **User** – searches for available treks, views trek information, makes bookings, and manages their bookings.

The backend is built using Flask, while **Flask-SQLAlchemy** is used to work with the SQLite database and **Flask-Login** handles authentication and sessions.

---

## ✨ Main Features

### 🔐 Authentication & Account Management

- User registration and login
- Logout functionality
- Passwords are stored using Werkzeug password hashing
- Separate login flow for admin, staff, and normal users
- Username and email uniqueness checks
- Basic backend validation for registration
- Minimum password length validation
- Blacklisted users are prevented from logging in
- Staff accounts require admin approval before they can access staff features

### 👑 Admin Dashboard

The admin gets the highest level of access in the system.

The dashboard provides an overview of:

- Total treks
- Total users
- Total staff
- Total bookings
- Pending staff approvals
- Trek status distribution
- Booking status distribution
- Most-booked treks

The dashboard also provides a quick way to understand what is happening in the system without manually checking every record.

### 🥾 Trek Management

Admins can:

- Create new treks
- Edit existing treks
- Delete treks
- Set trek locations
- Set trek difficulty
- Set trek duration
- Define total and available slots
- Add trek descriptions
- Set start and end dates
- Change trek status
- Assign approved staff members to treks

Trek statuses supported by the application include:

- `Pending`
- `Open`
- `Closed`
- `Completed`

Difficulty levels include:

- `Easy`
- `Moderate`
- `Hard`

### 👥 User Management

Admins can:

- View registered users
- Search users by username or email
- View user information
- Blacklist users
- Remove a blacklist restriction

A blacklisted user cannot log into the system until the restriction is removed.

### 🧑‍💼 Staff Management

Staff members have their own workflow.

When someone registers as staff:

1. A staff account is created.
2. A staff profile is created.
3. The account remains pending.
4. An admin reviews the account.
5. The admin can approve the staff member.
6. Only after approval can the staff member access the staff dashboard.

Admins can also blacklist or unblacklist staff accounts.

### 🗺️ Staff Trek Management

Approved staff members can see the treks assigned to them.

For an assigned trek, staff can:

- View trek information
- View participants
- Update available slots
- Change trek status
- Mark a trek as completed

When a trek is marked as **Completed**, active bookings for that trek are also marked as completed.

Staff members cannot manage treks that have not been assigned to them.

### 🎟️ Trek Booking

Normal users can:

- Browse open treks
- Search treks
- Filter by location
- Filter by difficulty
- View available slots
- Book a trek
- View their bookings
- Cancel bookings

The system also prevents a user from booking the same trek multiple times while they already have an active booking.

When a booking is made:

```text
Available slots = Available slots - 1
```

When a booking is cancelled:

```text
Available slots = Available slots + 1
```

This keeps the slot count connected to the booking system.

### 🔎 Search & Filtering

The project includes search functionality in multiple parts of the application.

Users can search/filter treks by:

- Trek name
- Location
- Difficulty

Admins can search:

- Treks
- Users
- Staff

The backend uses SQLAlchemy queries and case-insensitive matching where appropriate.

### 📊 Dashboard Statistics

The application calculates useful statistics from the database, including:

- Number of users
- Number of staff members
- Number of treks
- Number of bookings
- Trek status distribution
- Booking status distribution
- Most-booked treks
- User booking status distribution

These statistics are used to make the dashboards more informative.

---

## 🧱 Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Main programming language |
| **Flask** | Web application framework |
| **Flask-SQLAlchemy** | Database ORM |
| **SQLite** | Database |
| **Flask-Login** | Authentication and session management |
| **Werkzeug** | Password hashing and security utilities |
| **Jinja2** | Dynamic HTML templating |
| **HTML/CSS** | Frontend structure and styling |
| **OpenAPI 3.0** | REST API documentation |

---

## 🏗️ Application Architecture

The project follows a simple modular Flask structure instead of putting everything into one file.

The main parts are:

```text
Browser
   │
   ▼
Flask Routes
   │
   ├── Authentication
   ├── Admin Routes
   ├── Staff Routes
   ├── User Routes
   │
   ▼
SQLAlchemy Models
   │
   ▼
SQLite Database
```

There is also a separate API layer:

```text
API Client
    │
    ▼
/api/*
    │
    ▼
API Routes
    │
    ▼
SQLAlchemy Models
    │
    ▼
SQLite Database
```

---

## 📁 Project Structure

```text
project/
│
├── app.py
├── api_routes.py
├── routes.py
├── models.py
├── extensions.py
├── config.py
├── create_admin.py
├── api.yaml
├── requirements.txt
│
├── instance/
│   └── trekking.db
│
├── templates/
│   ├── base.html
│   │
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   │
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── treks.html
│   │   ├── trek_form.html
│   │   ├── users.html
│   │   ├── staff.html
│   │   ├── bookings.html
│   │   └── search.html
│   │
│   ├── staff/
│   │   ├── dashboard.html
│   │   └── trek_detail.html
│   │
│   └── user/
│       ├── dashboard.html
│       ├── treks.html
│       ├── bookings.html
│       └── profile.html
│
└── static/
```

### Important files

**`app.py`**

Creates and configures the Flask application, initializes the database and login manager, creates database tables, seeds the default admin account, and registers the web and API blueprints.

**`routes.py`**

Contains the main browser-facing routes, including authentication, admin functionality, staff functionality, user functionality, trek management, and bookings.

**`api_routes.py`**

Contains REST API endpoints for treks, users, bookings, and statistics.

**`models.py`**

Defines the database models and their relationships.

**`extensions.py`**

Keeps Flask-SQLAlchemy and Flask-Login extensions separate from the application setup.

**`config.py`**

Contains application configuration such as the secret key and SQLite database location.

**`create_admin.py`**

Creates the initial admin account if one does not already exist.

**`api.yaml`**

Contains the OpenAPI 3.0 documentation for the REST API.

---

## 🗄️ Database Design

The application uses SQLite with SQLAlchemy ORM.

There are four main models.

### 1. User

Stores account information.

Important fields include:

- `id`
- `username`
- `email`
- `password_hash`
- `role`
- `is_blacklisted`
- `created_at`

Supported roles:

```text
admin
staff
user
```

### 2. Trek

Stores information about each trek.

Important fields include:

- `name`
- `location`
- `difficulty`
- `duration`
- `total_slots`
- `available_slots`
- `status`
- `start_date`
- `end_date`
- `description`
- `assigned_staff_id`

### 3. Booking

Connects users with treks.

It stores:

- User ID
- Trek ID
- Booking date
- Booking status

Booking statuses include:

```text
Booked
Cancelled
Completed
```

### 4. StaffProfile

Stores additional information for staff accounts, including:

- Contact information
- Experience
- Approval status
- Joining date

---

## 🔗 Model Relationships

The database relationships can be understood as:

```text
User
 │
 ├───────────────► Booking ◄─────────────── Trek
 │
 └───────────────► StaffProfile
```

A user can have multiple bookings.

A trek can have multiple bookings.

A staff user can have one staff profile.

A trek can also have an assigned staff member.

---

## 🚀 Running the Project Locally

### 1. Prerequisites

Make sure you have:

- Python 3 installed
- pip installed
- A terminal
- A web browser

You can check Python with:

```bash
python3 --version
```

---

### 2. Open the project directory

```bash
cd "project root folder"
```

---

### 3. Create a virtual environment

It is recommended to create the virtual environment outside the submitted project ZIP or exclude it from the submission.

```bash
python3 -m venv venv
```

---

### 4. Activate the environment

#### Linux/macOS

```bash
source venv/bin/activate
```

#### Windows

```powershell
venv\Scripts\activate
```

---

### 5. Install dependencies

The required packages are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

The current requirements include:

```text
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.1.8
```

---

### 6. Start the application

```bash
python3 app.py
```

The Flask development server runs on:

```text
http://127.0.0.1:5000/
```

Open that address in your browser.

---

## 🔑 Default Admin Account

The application automatically creates an admin account when the database is initialized and an admin account does not already exist.

Default credentials:

```text
Username: admin
Password: admin123
Email: admin@trek.com
```

> **Note:** These credentials are intended for local development/demo use. A real deployment should use a strong password and a secret key stored securely in environment variables.

---

## 👤 Typical User Flow

A normal user can follow this flow:

```text
Register
   ↓
Login
   ↓
User Dashboard
   ↓
Browse Treks
   ↓
Search / Filter
   ↓
Select an Open Trek
   ↓
Book Trek
   ↓
View Booking
   ↓
Cancel Booking if required
```

The application automatically checks whether the trek is open and whether slots are still available before creating a booking.

---

## 🧑‍💼 Typical Staff Flow

```text
Register as Staff
       ↓
Wait for Admin Approval
       ↓
Admin Approves Account
       ↓
Staff Login
       ↓
Staff Dashboard
       ↓
View Assigned Treks
       ↓
Manage Slots / Status
       ↓
View Participants
```

Staff access is restricted until approval is completed.

---

## 👑 Typical Admin Flow

```text
Admin Login
     ↓
Admin Dashboard
     │
     ├── Manage Treks
     ├── Manage Users
     ├── Manage Staff
     ├── View Bookings
     ├── Search Records
     └── View Statistics
```

The admin can also assign approved staff members to particular treks.

---

# 🌐 REST API

The project includes a REST API under:

```text
/api
```

The API is documented using OpenAPI 3.0 in:

```text
api.yaml
```

### Available API areas

#### Treks

```text
GET    /api/treks
GET    /api/treks/<id>
POST   /api/treks
PUT    /api/treks/<id>
DELETE /api/treks/<id>
```

The trek listing endpoint supports filters such as:

```text
/api/treks?status=Open
/api/treks?difficulty=Easy
/api/treks?location=Manali
```

#### Users

```text
GET /api/users
GET /api/users/<id>
```

User management endpoints require appropriate authentication and admin access.

#### Bookings

```text
GET    /api/bookings
POST   /api/bookings
GET    /api/bookings/<id>
DELETE /api/bookings/<id>
```

#### Statistics

```text
GET /api/stats
```

The statistics endpoint provides admin dashboard information such as total users, staff, treks, bookings, and status counts.

---

## 🔒 Access Control

Access control is handled on the server side using Flask-Login and custom role decorators.

The application has separate access checks for:

```text
admin_required
staff_required
user_required
```

This means that simply knowing a URL is not enough to access protected pages.

For example:

- A normal user cannot access admin pages.
- An unapproved staff member cannot access staff pages.
- A staff member cannot manage a trek assigned to someone else.
- Users cannot access another user's private booking information through the API.

---

## ✅ Validation & Business Rules

Several checks are performed on the backend to keep the data consistent.

Examples include:

- Required registration fields must be provided.
- Usernames must be at least 3 characters.
- Passwords must be at least 6 characters.
- Password confirmation must match.
- Duplicate usernames are rejected.
- Duplicate emails are rejected.
- Trek difficulty must be valid.
- Trek duration must be at least one day.
- Trek slots must be positive.
- Trek end date cannot be before the start date.
- Users cannot book closed or completed treks.
- Users cannot book a trek when there are no slots.
- Users cannot create duplicate active bookings for the same trek.
- Booking cancellation restores one available slot.
- Staff cannot set available slots below zero or above total slots.
- Only approved staff can access staff functionality.
- Blacklisted accounts cannot log in.

These checks are intentionally performed on the backend instead of relying only on browser-side validation.

---

## 🧪 Testing the Application

A simple manual testing flow can be used to verify the main functionality.

### Authentication

- Register a normal user.
- Log in with the new account.
- Try an incorrect password.
- Log out.
- Register a staff account.
- Confirm that staff access is blocked until approval.

### Admin

- Log in as admin.
- Create a trek.
- Edit the trek.
- Assign an approved staff member.
- Search for users/treks.
- Approve a staff account.
- View bookings.
- Blacklist/unblacklist an account.

### User

- Log in as a normal user.
- Search for an open trek.
- Book the trek.
- Check the booking list.
- Confirm that available slots decrease.
- Cancel the booking.
- Confirm that the available slot count increases.

### Staff

- Log in using an approved staff account.
- Open the assigned trek.
- Update available slots.
- Change the trek status.
- View participants.
- Mark the trek as completed.

### API

API endpoints can be tested using tools such as:

- Postman
- Insomnia
- cURL
- Browser (for simple GET requests)

The endpoint definitions and request/response structure are described in `api.yaml`.

---

## 🧠 What I Learned From This Project

This project helped put several backend and web development concepts together instead of treating them as separate topics.

Some of the main concepts involved are:

- Flask application structure
- Routing and HTTP methods
- Authentication and sessions
- Role-based authorization
- Password hashing
- SQLAlchemy ORM
- Database relationships
- CRUD operations
- Form handling
- Backend validation
- REST API development
- OpenAPI documentation
- Jinja2 templates
- Managing application state
- Handling real booking constraints
- Organizing a Flask project into separate modules

One of the more useful parts of the project was connecting the different pieces together. For example, a booking is not just a new database row — it also affects the number of available slots, appears in the user's dashboard, and can later be cancelled or completed.

---

## 🔮 Possible Future Improvements

There are several areas where the project could be extended in the future:

- Add trek images and richer trek descriptions
- Add email notifications for bookings
- Add password reset functionality
- Add pagination for large datasets
- Add stronger API authentication such as token-based authentication
- Add automated unit and integration tests
- Add database migrations using Flask-Migrate
- Add deployment configuration for production
- Add a payment system for paid treks
- Add reviews and ratings for completed treks
- Add more detailed staff scheduling
- Improve analytics with more dashboard charts
- Add a dedicated trek detail page with maps and route information

---

## ⚠️ Notes for Development

The project is configured for local development.

The Flask application currently runs with:

```python
debug=True
```

For production deployment, debug mode should be disabled.

The secret key in `config.py` also contains a development fallback. For an actual deployment, it should be provided through an environment variable.

---

## 📄 License / Academic Use

This project was developed for **educational and academic purposes**.

It is intended to demonstrate concepts related to:

- Flask web development
- Database management
- Authentication
- Role-based access
- REST APIs
- CRUD operations
- Backend application design

---

## 👨‍💻 Author

**Tanmay Sharma**

Developed as an academic project with a focus on building a practical web application using Flask, SQLAlchemy, SQLite, and REST APIs.

---

## ⭐ Final Note

The main goal of this project was not just to make a website where a user can click a "Book" button. The idea was to build the basic workflow that a real trek-management platform would need: different user roles, staff approval, trek assignment, limited slots, booking management, cancellation, status updates, search, and an API layer.

There is still plenty of room to improve it, but the current version provides a solid foundation for expanding the application into a more complete trekking platform.
