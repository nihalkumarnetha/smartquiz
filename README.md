# SmartQuiz - Online Quiz Management System

A comprehensive web-based quiz management system built with Flask, allowing admins, lecturers, and students to manage and take quizzes.

## Features

### Admin Features
- Dashboard with system statistics
- User management (view all users)
- Quiz and results reports
- System overview

### Lecturer Features
- Create and manage quizzes
- Add questions with multiple choice options
- View quiz analytics
- Manage question banks

### Student Features
- Browse available quizzes
- Take quizzes with timed sessions
- View quiz results and scores
- Track quiz history

## Installation

1. **Install Python requirements:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Access the application:**
Open your browser and navigate to `http://localhost:5000`

## Default Login Credentials

- **Username:** admin
- **Password:** admin123
- **Role:** Admin

## Creating New Users

1. Click "Sign Up" on the login page
2. Fill in the registration form
3. Choose your role (Student or Lecturer)
4. Complete registration and log in

## Project Structure

```
smartquiz/
├── .smartquiz/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── smartquiz.db          # SQLite database (auto-created)
│   └── templates/
│       ├── base.html          # Base template with navbar
│       ├── Student_Login.html # Student login page
│       ├── Lecturer_Login.html# Lecturer login page
│       ├── Admin_Login.html   # Admin login page
│       ├── signup.html        # Registration page
│       ├── admin_dashboard.html
│       ├── admin_users.html
│       ├── admin_reports.html
│       ├── lecturer_dashboard.html
│       ├── create_quiz.html
│       ├── add_questions.html
│       ├── student_dashboard.html
│       ├── take_quiz.html
│       └── result_details.html
└── htmls/                     # Legacy HTML files
```

## Database Schema

- **users:** User accounts with roles (admin, lecturer, student)
- **quizzes:** Quiz information created by lecturers
- **questions:** Questions for each quiz with multiple choice options
- **results:** Quiz completion records with scores

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- CSRF protection with Flask sessions

## Future Enhancements

- Quiz timer functionality
- Email notifications
- Advanced analytics and charts
- Question import/export
- User profile management
- Quiz scheduling
- Leaderboards

## License

This project is free to use for educational purposes.
"# smartquiz" 
