"""
SmartQuiz - SQLite Version for Replit
This version uses SQLite instead of MySQL for easier deployment on Replit
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '.smartquiz', 'templates')
HTMLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'htmls')
DB_PATH = 'smartquiz.db'

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=None)
app.secret_key = os.getenv('SECRET_KEY', 'smartquiz-secret-key-2025')

def dict_factory(cursor, row):
    """Convert database row to dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn

def init_db():
    """Initialize database and create tables"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          username TEXT UNIQUE NOT NULL, 
                          password TEXT NOT NULL,
                          role TEXT NOT NULL, 
                          email TEXT, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Quizzes table
        cursor.execute('''CREATE TABLE IF NOT EXISTS quizzes
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          title TEXT NOT NULL, 
                          description TEXT,
                          created_by INTEGER NOT NULL, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                          duration INTEGER,
                          FOREIGN KEY(created_by) REFERENCES users(id))''')
        
        # Questions table
        cursor.execute('''CREATE TABLE IF NOT EXISTS questions
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          quiz_id INTEGER NOT NULL, 
                          question TEXT NOT NULL,
                          option_a TEXT, 
                          option_b TEXT, 
                          option_c TEXT, 
                          option_d TEXT,
                          correct_answer TEXT, 
                          FOREIGN KEY(quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE)''')
        
        # Results table
        cursor.execute('''CREATE TABLE IF NOT EXISTS results
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          user_id INTEGER NOT NULL, 
                          quiz_id INTEGER NOT NULL,
                          score INTEGER, 
                          total_questions INTEGER, 
                          completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY(user_id) REFERENCES users(id),
                          FOREIGN KEY(quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE)''')
        
        # Notifications table
        cursor.execute('''CREATE TABLE IF NOT EXISTS notifications
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          title TEXT, 
                          message TEXT, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Courses table
        cursor.execute('''CREATE TABLE IF NOT EXISTS courses
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          name TEXT NOT NULL, 
                          description TEXT, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Review submissions table
        cursor.execute('''CREATE TABLE IF NOT EXISTS review_submissions
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          user_id INTEGER NOT NULL, 
                          title TEXT, 
                          details TEXT,
                          status TEXT DEFAULT 'pending', 
                          submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')
        
        conn.commit()
        
        # Create default admin user if it doesn't exist
        cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
        if not cursor.fetchone():
            admin_password = generate_password_hash('admin123')
            cursor.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                          ('admin', admin_password, 'admin', 'admin@smartquiz.com'))
            conn.commit()
        
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.before_request
def before_request():
    """Initialize database before each request"""
    init_db()

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'lecturer':
            return redirect(url_for('lecturer_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle user login"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Username and password required', 'danger')
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome {user["username"]}!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'lecturer':
                return redirect(url_for('lecturer_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Login error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user registration"""
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'student')
    email = request.form.get('email', '')
    
    if not username or not password:
        flash('Username and password required', 'danger')
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash('Username already exists', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                      (username, hashed_password, role, email))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Signup error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get stats
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM quizzes")
        quiz_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM results")
        result_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return render_template('AdminDashboard.jsp', 
                             user_count=user_count,
                             quiz_count=quiz_count,
                             result_count=result_count)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/admin/users')
def admin_users():
    """View all users"""
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, email, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('admin_users.html', users=users)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

# ==================== LECTURER ROUTES ====================

@app.route('/lecturer/dashboard')
def lecturer_dashboard():
    """Lecturer dashboard"""
    if 'user_id' not in session or session['role'] != 'lecturer':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, created_at FROM quizzes WHERE created_by = ? ORDER BY created_at DESC", 
                      (session['user_id'],))
        quizzes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('LecturerDashboard.jsp', quizzes=quizzes)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/lecturer/create-quiz', methods=['GET', 'POST'])
def create_quiz():
    """Create a new quiz"""
    if 'user_id' not in session or session['role'] != 'lecturer':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration', 60, type=int)
        
        if not title:
            flash('Quiz title required', 'danger')
            return redirect(url_for('create_quiz'))
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO quizzes (title, description, created_by, duration) VALUES (?, ?, ?, ?)",
                          (title, description, session['user_id'], duration))
            conn.commit()
            quiz_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            flash('Quiz created successfully!', 'success')
            return redirect(url_for('add_questions', quiz_id=quiz_id))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('lecturer_dashboard'))
    
    return render_template('CreateQuiz.jsp')

# ==================== STUDENT ROUTES ====================

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard"""
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM quizzes")
        quizzes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('student_dashboard.html', quizzes=quizzes)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
