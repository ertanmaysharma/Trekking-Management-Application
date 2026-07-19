# 🎓 Student Enrollment Management System

A Flask-based web application for managing student records and course enrollments. The project allows users to perform complete CRUD (Create, Read, Update, Delete) operations on student data while maintaining course enrollment information using a SQLite database.

## ✨ Features

- ➕ Add new students
- 📋 View all enrolled students
- 👤 View individual student details
- ✏️ Update student information
- 🗑️ Delete students and their enrollments
- ✅ Prevent duplicate roll numbers
- 📚 Manage course enrollments
- 💾 SQLite database integration
- 🌐 Dynamic web pages using Jinja2 templates

## 🛠️ Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Jinja2
- HTML5

## 📂 Project Structure

```text
project/
│── app.py
│── database.sql
│── database.sqlite3
│── templates/
│   ├── index.html
│   ├── create.html
│   ├── update.html
│   ├── student.html
│   └── exists.html
│── static/
```

## 🚀 Installation

1. Clone the repository.

```bash
git clone https://github.com/your-username/student-enrollment-management.git
```

2. Navigate to the project folder.

```bash
cd student-enrollment-management
```

3. Create a virtual environment (optional but recommended).

```bash
python -m venv venv
```

4. Activate the virtual environment.

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

5. Install the required packages.

```bash
pip install flask flask-sqlalchemy
```

6. Create the database using the SQL script.

```bash
sqlite3 database.sqlite3 < database.sql
```

7. Run the Flask application.

```bash
python app.py
```

8. Open your browser and visit:

```
http://127.0.0.1:5000/
```

## 🗄️ Database Schema

The application consists of three tables:

- **Student**
- **Course**
- **Enrollments**

The Course table is pre-populated with four predefined courses:

| Course Code | Course Name |
|-------------|-------------|
| CSE01 | MAD I |
| CSE02 | DBMS |
| CSE03 | PDSA |
| BST13 | BDM |

## 📸 Application Pages

- Home Page
- Add Student
- Update Student
- Student Details
- Duplicate Roll Number Page

## 📖 Learning Outcomes

This project demonstrates:

- Flask routing
- CRUD operations
- SQLAlchemy ORM
- One-to-Many relationships
- SQLite database management
- Form handling
- Jinja2 templating
- Basic web application development

## 📄 License

This project was developed for educational purposes as part of a **Modern Application Development (MAD-I)** laboratory assignment.
