from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'smartquiz-secret-key-2025')
app.config['SECRET_KEY'] = app.secret_key
app.config['SESSION_TIMEOUT'] = 1800  # 30 minutes session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['SESSION_COOKIE_NAME'] = 'smartquiz_session'

# ==================== SESSION MANAGEMENT (FIXED) ====================

@app.before_request
def make_session_permanent():
    """Make all sessions permanent and set cache control headers"""
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    
    if 'user_id' in session:
        
        pass  

@app.after_request
def set_cache_control(response):
    """Set cache control headers based on authentication status"""
    if 'user_id' in session:
        
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0' # <-- MODIFIED
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        # Indicate response may vary based on cookies
        existing_vary = response.headers.get('Vary')
        if existing_vary:
            if 'Cookie' not in [h.strip() for h in existing_vary.split(',')]:
                response.headers['Vary'] = existing_vary + ', Cookie'
        else:
            response.headers['Vary'] = 'Cookie'
    else:
        # Public pages: allow public cache
        response.headers['Cache-Control'] = 'public, max-age=3600'
    
    # Ensure all HTML files are treated correctly
    if 'text/html' in response.content_type:
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
    return response


def session_required(role=None):
    """Decorator to require active session and optional role check"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Session expired. Please log in again.', 'error')
                return redirect(url_for('login'))
            
            if role and session.get('role') != role:
                flash('Unauthorized access', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/session_status')
def session_status():
    """Simple endpoint used by client-side JS to verify whether server-side session is still active."""
    # Return uncached response so browsers / proxies don't cache session state
    if 'user_id' in session:
        resp = jsonify({'status': 'ok'})
        resp.status_code = 200
    else:
        resp = jsonify({'status': 'expired'})
        resp.status_code = 401

    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    # Vary by Cookie to prevent intermediaries from serving stale results
    resp.headers['Vary'] = 'Cookie'
    return resp
# The 'no_cache' decorator definition you had can be removed, as the logic is now in @app.after_request and the explicit logout.
# def no_cache(view):
#     @wraps(view)
#     # ... (as defined above) ...
#     def decorated_view(*args, **kwargs):
#         response = view(*args, **kwargs)
#         if isinstance(response, Response):
#             response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#             response.headers['Pragma'] = 'no-cache'
#             response.headers['Expires'] = '0'
#         return response
#     return decorated_view

# MySQL Configuration
# ... (DB_CONFIG remains the same) ...
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin@123',
    'database': 'smartquiz'
}

# ... (init_db, get_db, init_db_on_request remain the same) ...

# Initialize database and create tables
def init_db():
    try:
        # Connect to MySQL without database first to create it
        temp_config = {
            'host': DB_CONFIG['host'],
            'user': DB_CONFIG['user'],
            'password': DB_CONFIG['password']
        }
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        conn.close()
        
        # Now connect to the actual database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INT AUTO_INCREMENT PRIMARY KEY, 
                          username VARCHAR(255) UNIQUE NOT NULL, 
                          password VARCHAR(255) NOT NULL,
                          role VARCHAR(50) NOT NULL, 
                          email VARCHAR(255), 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Quizzes table
        cursor.execute('''CREATE TABLE IF NOT EXISTS quizzes
                         (id INT AUTO_INCREMENT PRIMARY KEY, 
                          title VARCHAR(255) NOT NULL, 
                          description TEXT,
                          created_by INT NOT NULL, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                          duration INT,
                          FOREIGN KEY(created_by) REFERENCES users(id))''')
        
        # Questions table
        cursor.execute('''CREATE TABLE IF NOT EXISTS questions
                         (id INT AUTO_INCREMENT PRIMARY KEY, 
                          quiz_id INT NOT NULL, 
                          question TEXT NOT NULL,
                          option_a VARCHAR(255), 
                          option_b VARCHAR(255), 
                          option_c VARCHAR(255), 
                          option_d VARCHAR(255),
                          correct_answer VARCHAR(1), 
                          FOREIGN KEY(quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE)''')
        
        # Results table
        cursor.execute('''CREATE TABLE IF NOT EXISTS results
                         (id INT AUTO_INCREMENT PRIMARY KEY, 
                          user_id INT NOT NULL, 
                          quiz_id INT NOT NULL,
                          score INT, 
                          total_questions INT, 
                          completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY(user_id) REFERENCES users(id),
                          FOREIGN KEY(quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE)''')
        
        # Notifications table
        cursor.execute('''CREATE TABLE IF NOT EXISTS notifications
                         (id INT AUTO_INCREMENT PRIMARY KEY, 
                          title VARCHAR(255), 
                          message TEXT, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Courses table
        cursor.execute('''CREATE TABLE IF NOT EXISTS courses
                         (id INT AUTO_INCREMENT PRIMARY KEY, 
                          name VARCHAR(255) NOT NULL, 
                          description TEXT, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        
        
        conn.commit()
        
        # Check if admin user exists, if not create it
        cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
        if not cursor.fetchone():
            admin_password = generate_password_hash('admin123')
            cursor.execute("INSERT INTO users (username, password, role, email) VALUES (%s, %s, %s, %s)",
                          ('admin', admin_password, 'admin', 'admin@smartquiz.com'))
            conn.commit()
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Keep the database initialization in before_request (called on every request)
@app.before_request
def init_db_on_request():
    init_db()

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'lecturer':
            return redirect(url_for('lecturer_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    # Fetch courses from database
    courses = []
    try:
        conn = get_db()
        if conn:
            c = conn.cursor(dictionary=True)
            c.execute("SELECT id, name, description FROM courses ORDER BY created_at DESC LIMIT 10")
            courses = c.fetchall()
            c.close()
            conn.close()
    except Exception as e:
        print(f"Error fetching courses: {e}")
    
    # Serve the template index.html as the landing page
    return render_template('index.html', courses=courses)

@app.route('/Admin_Login.html')
def admin_login_html():
    return render_template('Admin_Login.html')

@app.route('/Lecturer_Login.html')
def lecturer_login_html():
    return render_template('Lecturer_Login.html')

@app.route('/Student_Login.html')
def student_login_html():
    return render_template('Student_Login.html')

@app.route('/signup.html')
def signup_html():
    return render_template('signup.html')

# Serve CSS, JS, and Images from htmls folder
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '../../htmls/css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '../../htmls/js'), filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '../../htmls/images'), filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session.permanent = True
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']  # Use role from database, not from form
                session['login_time'] = datetime.now().isoformat()
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
        else:
            flash('Database connection error', 'error')
    
    # For GET requests, redirect users to the landing page which already
    # provides role-specific login pages (Student/Admin/Lecturer).
    # POST handling above remains unchanged (forms on role pages still submit to /login).
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup.html'))
        
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            try:
                hashed_password = generate_password_hash(password)
                cursor.execute("INSERT INTO users (username, password, role, email) VALUES (%s, %s, %s, %s)",
                              (username, hashed_password, role, email))
                conn.commit()
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            except mysql.connector.Error as err:
                if err.errno == 1062:  # Duplicate username
                    flash('Username already exists', 'error')
                else:
                    flash(f'Error: {err}', 'error')
            finally:
                cursor.close()
                conn.close()
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()

    # 1. Create the redirect response object first
    response = redirect(url_for('index'))

    # 2. Apply the most aggressive no-cache headers to the redirect response.
    # This is CRITICAL for clearing the browser's BFCache history state for the previous page.
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Ensure the session cookie is removed from the browser immediately
    cookie_name = app.config.get('SESSION_COOKIE_NAME', 'session')
    # Delete both the configured cookie name and the default 'session'
    response.delete_cookie(cookie_name, path='/')
    response.delete_cookie('session', path='/')

    flash('You have been logged out', 'info')
    return response # <-- MODIFIED

# ==================== ADMIN ROUTES ====================
# ... (All other routes remain the same) ...

@app.route('/admin')
def admin():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
@session_required(role='admin')
def admin_dashboard():
    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT COUNT(*) as count FROM users WHERE role='student'")
    students = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM users WHERE role='lecturer'")
    lecturers = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM quizzes")
    quizzes = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM results")
    results = c.fetchone()['count']
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         students=students, lecturers=lecturers, 
                         quizzes=quizzes, results=results)

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT id, username, email, role FROM users")
    users = c.fetchall()
    conn.close()
    
    return render_template('admin_users.html', users=users)


@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@session_required(role='admin')
def admin_edit_user(user_id):
    conn = get_db()
    c = conn.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            if password:
                hashed = generate_password_hash(password)
                c.execute("UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s", (username, email, hashed, user_id))
            else:
                c.execute("UPDATE users SET username=%s, email=%s WHERE id=%s", (username, email, user_id))
            conn.commit()
            flash('User updated successfully.', 'success')
        except Error as e:
            conn.rollback()
            flash(f'Error updating user: {e}', 'error')
        finally:
            c.close()
            conn.close()
        return redirect(url_for('admin_users'))

    # GET
    c.execute("SELECT id, username, email, role FROM users WHERE id = %s", (user_id,))
    user = c.fetchone()
    c.close()
    conn.close()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin_users'))

    template = 'EditLecturer.html' if user['role'] == 'lecturer' else 'EditStudent.html'
    return render_template(template, user=user, error=None)


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@session_required(role='admin')
def admin_delete_user(user_id):

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash('User deleted.', 'info')
    except Error as e:
        conn.rollback()
        flash(f'Error deleting user: {e}', 'error')
    finally:
        c.close()
        conn.close()
    return redirect(url_for('admin_users'))

@app.route('/admin/reports')
@session_required(role='admin')
def admin_reports():
    
    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute("""SELECT u.username, q.title, r.score, r.total_questions, r.completed_at 
                 FROM results r 
                 JOIN users u ON r.user_id = u.id 
                 JOIN quizzes q ON r.quiz_id = q.id
                 ORDER BY r.completed_at DESC""")
    reports = c.fetchall()
    conn.close()
    
    return render_template('admin_reports.html', reports=reports)

# -------------------- Admin: Pending approvals / Approve/Reject --------------------
@app.route('/admin/pending')
@session_required(role='admin')
def admin_pending():

    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT id, username, email, role, created_at FROM users WHERE role = 'pending'")
    pending = c.fetchall()
    conn.close()
    return render_template('admin_pending.html', pending=pending)

@app.route('/admin/approve_user/<int:user_id>', methods=['POST'])
@session_required(role='admin')
def admin_approve_user(user_id):

    new_role = request.form.get('role', 'student')
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    conn.commit()
    conn.close()
    flash('User approved.', 'success')
    return redirect(url_for('admin_pending'))

@app.route('/admin/reject_user/<int:user_id>', methods=['POST'])
@session_required(role='admin')
def admin_reject_user(user_id):

    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    flash('User rejected and removed.', 'info')
    return redirect(url_for('admin_pending'))

# -------------------- Admin: Notifications --------------------
@app.route('/admin/notifications', methods=['GET', 'POST'])
@session_required(role='admin')
def admin_notifications():

    conn = get_db()
    c = conn.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        c.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", (title, message))
        conn.commit()
        flash('Notification created.', 'success')

    c.execute("SELECT * FROM notifications ORDER BY created_at DESC")
    notes = c.fetchall()
    conn.close()
    return render_template('admin_notifications.html', notes=notes)


@app.route('/admin/notification/<int:notification_id>/delete', methods=['POST'])
@session_required(role='admin')
def admin_delete_notification(notification_id):
    

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM notifications WHERE id = %s", (notification_id,))
        conn.commit()
        flash('Notification deleted.', 'info')
    except Error as e:
        conn.rollback()
        flash(f'Error deleting notification: {e}', 'error')
    finally:
        c.close()
        conn.close()
    return redirect(url_for('admin_notifications'))

# -------------------- Admin: Course Management --------------------
@app.route('/admin/courses', methods=['GET', 'POST'])
@session_required(role='admin')
def admin_courses():

    conn = get_db()
    c = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        c.execute("INSERT INTO courses (name, description) VALUES (%s, %s)", (name, description))
        conn.commit()
        flash('Course added.', 'success')

    c.execute("SELECT * FROM courses ORDER BY created_at DESC")
    courses = c.fetchall()
    conn.close()
    return render_template('admin_courses.html', courses=courses)


@app.route('/admin/course/<int:course_id>/delete', methods=['POST'])
@session_required(role='admin')
def admin_delete_course(course_id):
    

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM courses WHERE id = %s", (course_id,))
        conn.commit()
        flash('Course deleted.', 'info')
    except Error as e:
        conn.rollback()
        flash(f'Error deleting course: {e}', 'error')
    finally:
        c.close()
        conn.close()
    return redirect(url_for('admin_courses'))

   
   

# ==================== LECTURER ROUTES ====================

@app.route('/lecturer/dashboard')
@session_required(role='lecturer')
def lecturer_dashboard():
    
    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM quizzes WHERE created_by = %s", (session['user_id'],))
    quizzes = c.fetchall()

    # Additional metrics for lecturer: total questions across quizzes and distinct students who attempted those quizzes
    c.execute("SELECT COUNT(q.id) as total_questions FROM questions q JOIN quizzes qu ON q.quiz_id = qu.id WHERE qu.created_by = %s", (session['user_id'],))
    total_questions_row = c.fetchone()
    total_questions = total_questions_row['total_questions'] if total_questions_row else 0

    c.execute("SELECT COUNT(DISTINCT r.user_id) as total_students FROM results r JOIN quizzes qu ON r.quiz_id = qu.id WHERE qu.created_by = %s", (session['user_id'],))
    total_students_row = c.fetchone()
    total_students = total_students_row['total_students'] if total_students_row else 0

    conn.close()
    
    return render_template('lecturer_dashboard.html', quizzes=quizzes, total_questions=total_questions, total_students=total_students)

@app.route('/lecturer/create-quiz', methods=['GET', 'POST'])
@session_required(role='lecturer')
def create_quiz():
    
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration', 30)
        
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO quizzes (title, description, created_by, duration) VALUES (%s, %s, %s, %s)",
                  (title, description, session['user_id'], duration))
        conn.commit()
        quiz_id = c.lastrowid
        conn.close()
        
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('add_questions', quiz_id=quiz_id))
    
    return render_template('create_quiz.html')

@app.route('/lecturer/quiz/<int:quiz_id>/questions', methods=['GET', 'POST'])
@session_required(role='lecturer')
def add_questions(quiz_id):
    
    conn = get_db()
    c = conn.cursor()
    
    # 1. Fetch the current count of questions
    c.execute("SELECT COUNT(id) FROM questions WHERE quiz_id = %s", (quiz_id,))
    current_question_count = c.fetchone()[0]
    
    MAX_QUESTIONS = 20

    if request.method == 'POST':
        # 2. Check and enforce the MAXIMUM limit
        if current_question_count >= MAX_QUESTIONS:
            conn.close() # Close connection before redirecting
            flash(f'Cannot add more questions. The maximum limit of {MAX_QUESTIONS} questions has been reached.', 'warning')
            return redirect(url_for('add_questions', quiz_id=quiz_id))
         
        
        # --- Continue with adding the question if the limit is NOT reached ---
        question = request.form.get('question')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        # ... (rest of form data) ...
        correct_answer = request.form.get('correct_answer')
        
        c.execute("INSERT INTO questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_answer) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                  (quiz_id, question, option_a, option_b, option_c, option_d, correct_answer))
        conn.commit()
        
        flash('Question added successfully!', 'success')
        # The count will be accurate upon the next load
        # No need to manually update current_question_count here since the GET logic handles the refresh
        
    # --- GET request logic (refreshed data) ---
    
    # Fetch questions list and quiz metadata
    c.execute("SELECT * FROM questions WHERE quiz_id = %s", (quiz_id,))
    questions = c.fetchall()
    
    c.execute("SELECT id, title, description, duration FROM quizzes WHERE id = %s", (quiz_id,))
    quiz = c.fetchone()
    
    conn.close() 
    
    if not quiz:
        flash('Quiz metadata not found.', 'error')
        return redirect(url_for('student_dashboard'))
        
    # Recalculate count if POST logic successfully added a question
    # This ensures the template shows the correct number immediately after POST
    current_question_count = len(questions)
 
    return render_template('add_questions.html', 
                           quiz_id=quiz_id, 
                           questions=questions, 
                           quiz=quiz,
                           current_count=current_question_count,
                           min_count=20, # Pass minimum to template for display
                           max_count=MAX_QUESTIONS)


@app.route('/lecturer/quiz/<int:quiz_id>/delete', methods=['POST'])
@session_required(role='lecturer')
def delete_quiz(quiz_id):
    conn = get_db()
    c = conn.cursor(dictionary=True)
    # Verify that the quiz belongs to this lecturer
    c.execute("SELECT id, created_by FROM quizzes WHERE id = %s", (quiz_id,))
    quiz = c.fetchone()
    
    if not quiz or quiz['created_by'] != session['user_id']:
        flash('You do not have permission to delete this quiz.', 'error')
        c.close()
        conn.close()
        return redirect(url_for('lecturer_dashboard'))
    
    # Delete quiz (questions will cascade delete due to ON DELETE CASCADE)
    try:
        c.execute("DELETE FROM quizzes WHERE id = %s", (quiz_id,))
        conn.commit()
        flash('Quiz deleted successfully.', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error deleting quiz: {e}', 'error')
    finally:
        c.close()
        conn.close()
    
    return redirect(url_for('lecturer_dashboard'))

# -------------------- Lecturer: Students List --------------------
@app.route('/lecturer/students')
@session_required(role='lecturer')
def lecturer_students():
    """View list of all students who attempted lecturer's quizzes"""
    conn = get_db()
    c = conn.cursor(dictionary=True)
    lecturer_id = session['user_id']

    # Get all students who have attempted any of this lecturer's quizzes
    c.execute("""
        SELECT DISTINCT u.id, u.username, u.email,
               COUNT(DISTINCT r.id) as total_attempts,
               COUNT(DISTINCT r.quiz_id) as quizzes_attempted,
               MAX(r.completed_at) as last_attempt,
               AVG(CAST(r.score AS FLOAT) / NULLIF(r.total_questions, 0)) * 100 as avg_score
        FROM users u
        JOIN results r ON u.id = r.user_id
        JOIN quizzes q ON r.quiz_id = q.id
        WHERE q.created_by = %s AND u.role = 'student'
        GROUP BY u.id, u.username, u.email
        ORDER BY MAX(r.completed_at) DESC
    """, (lecturer_id,))
    students = c.fetchall()

    # Count total unique quizzes by this lecturer
    c.execute("SELECT COUNT(*) as count FROM quizzes WHERE created_by = %s", (lecturer_id,))
    total_lecturer_quizzes = c.fetchone()['count']

    conn.close()

    return render_template(
        'lecturer_students.html',
        students=students,
        total_lecturer_quizzes=total_lecturer_quizzes
    )


# -------------------- Lecturer: Student Analytics --------------------
@app.route('/lecturer/student/<int:student_id>/analytics')
@session_required(role='lecturer')
def lecturer_student_analytics(student_id):
    """View detailed analytics for a specific student's performance on lecturer's quizzes"""
    conn = get_db()
    c = conn.cursor(dictionary=True)
    lecturer_id = session['user_id']

    # Verify student exists
    c.execute("SELECT id, username FROM users WHERE id = %s AND role='student'", (student_id,))
    student = c.fetchone()
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('lecturer_dashboard'))

    # Get all quizzes created by this lecturer
    c.execute("SELECT id, title FROM quizzes WHERE created_by = %s", (lecturer_id,))
    lecturer_quizzes = {q['id']: q['title'] for q in c.fetchall()}

    # Get all results for this student on lecturer's quizzes
    c.execute("""
        SELECT r.id, r.quiz_id, r.score, r.total_questions, r.completed_at, q.title
        FROM results r
        JOIN quizzes q ON r.quiz_id = q.id
        WHERE r.user_id = %s AND q.created_by = %s
        ORDER BY r.completed_at DESC
    """, (student_id, lecturer_id))
    student_results = c.fetchall()

    # Total attempts on this lecturer's quizzes
    total_attempts = len(student_results)

    # Calculate overall average score on lecturer's quizzes
    if total_attempts > 0:
        total_score = sum([r['score'] for r in student_results])
        total_questions = sum([r['total_questions'] for r in student_results])
        avg_score_pct = round((total_score / total_questions * 100) if total_questions > 0 else 0, 2)
    else:
        avg_score_pct = 0

    # Best performance
    best_score_pct = 0
    best_quiz_title = 'N/A'
    if student_results:
        best_result = max(student_results, key=lambda x: (x['score'] / x['total_questions']) if x['total_questions'] > 0 else 0)
        best_score_pct = round((best_result['score'] / best_result['total_questions'] * 100) if best_result['total_questions'] > 0 else 0, 2)
        best_quiz_title = best_result['title']

    # Quiz-by-quiz performance
    quiz_performance = []
    quiz_stats = {}
    for result in student_results:
        quiz_id = result['quiz_id']
        if quiz_id not in quiz_stats:
            quiz_stats[quiz_id] = {
                'title': result['title'],
                'attempts': 0,
                'scores': [],
                'dates': []
            }
        quiz_stats[quiz_id]['attempts'] += 1
        score_pct = round((result['score'] / result['total_questions'] * 100) if result['total_questions'] > 0 else 0, 2)
        quiz_stats[quiz_id]['scores'].append(score_pct)
        quiz_stats[quiz_id]['dates'].append(result['completed_at'])

    for quiz_id, stats in quiz_stats.items():
        quiz_performance.append({
            'title': stats['title'],
            'attempts': stats['attempts'],
            'best_score': max(stats['scores']) if stats['scores'] else 0,
            'avg_score': round(sum(stats['scores']) / len(stats['scores']), 2) if stats['scores'] else 0,
            'last_attempted': stats['dates'][0].strftime('%Y-%m-%d %H:%M') if stats['dates'] else 'N/A'
        })

    # Sort by most recent
    quiz_performance.sort(key=lambda x: x['last_attempted'], reverse=True)

    # Performance over time (last 15 attempts)
    recent_attempts = sorted(student_results, key=lambda x: x['completed_at'])[-15:]
    performance_data = {
        'labels': [r['completed_at'].strftime('%m-%d %H:%M') if hasattr(r['completed_at'], 'strftime') else str(r['completed_at']) for r in recent_attempts],
        'scores': [round((r['score'] / r['total_questions'] * 100) if r['total_questions'] > 0 else 0, 2) for r in recent_attempts]
    }

    # Score distribution
    score_counts = {'Excellent (80+)': 0, 'Good (60-79)': 0, 'Fair (40-59)': 0, 'Poor (<40)': 0}
    for result in student_results:
        score_pct = (result['score'] / result['total_questions'] * 100) if result['total_questions'] > 0 else 0
        if score_pct >= 80:
            score_counts['Excellent (80+)'] += 1
        elif score_pct >= 60:
            score_counts['Good (60-79)'] += 1
        elif score_pct >= 40:
            score_counts['Fair (40-59)'] += 1
        else:
            score_counts['Poor (<40)'] += 1

    distribution_data = {
        'labels': [k for k, v in score_counts.items() if v > 0] or ['No Data'],
        'values': [v for v in score_counts.values() if v > 0] or [0]
    }

    # Improvement trend (comparing first half vs second half attempts)
    improvement_trend = 0
    if len(student_results) >= 4:
        mid = len(student_results) // 2
        first_half = sorted(student_results, key=lambda x: x['completed_at'])[:mid]
        second_half = sorted(student_results, key=lambda x: x['completed_at'])[mid:]
        
        first_half_avg = sum([(r['score'] / r['total_questions']) for r in first_half]) / len(first_half) if first_half else 0
        second_half_avg = sum([(r['score'] / r['total_questions']) for r in second_half]) / len(second_half) if second_half else 0
        
        improvement_trend = round((second_half_avg - first_half_avg) * 100, 2)

    conn.close()

    return render_template(
        'lecturer_student_analytics.html',
        student_name=student['username'],
        student_id=student_id,
        total_attempts=total_attempts,
        avg_score_pct=avg_score_pct,
        best_score_pct=best_score_pct,
        best_quiz_title=best_quiz_title,
        improvement_trend=improvement_trend,
        quiz_performance=quiz_performance,
        performance_data=performance_data,
        distribution_data=distribution_data
    )

# -------------------- Lecturer: Notifications --------------------
@app.route('/lecturer/notifications', methods=['GET', 'POST'])
@session_required(role='lecturer')
def lecturer_notifications():
    conn = get_db()
    c = conn.cursor(dictionary=True)
    
    # Fetch notifications (admin broadcast notifications)
    c.execute("SELECT * FROM notifications ORDER BY created_at DESC LIMIT 20")
    notifications = c.fetchall()
    conn.close()
    
    return render_template('lecturer_notifications.html', notifications=notifications)

# ==================== STUDENT ROUTES ====================

# -------------------- Student: Analytics --------------------
@app.route('/student/analytics')
@session_required(role='student')
def student_analytics():
    """Personal analytics for the logged-in student"""
    conn = get_db()
    c = conn.cursor(dictionary=True)
    user_id = session['user_id']

    # Get all results for this student
    c.execute("""
        SELECT r.id, r.quiz_id, r.score, r.total_questions, r.completed_at, q.title
        FROM results r
        JOIN quizzes q ON r.quiz_id = q.id
        WHERE r.user_id = %s
        ORDER BY r.completed_at DESC
    """, (user_id,))
    all_results = c.fetchall()

    # Total quizzes attempted
    total_attempts = len(all_results)
    
    # Get total available quizzes
    c.execute("SELECT COUNT(*) as count FROM quizzes")
    total_quizzes_available = c.fetchone()['count']

    # Calculate overall average score
    if total_attempts > 0:
        total_score = sum([r['score'] for r in all_results])
        total_questions = sum([r['total_questions'] for r in all_results])
        avg_score_pct = round((total_score / total_questions * 100) if total_questions > 0 else 0, 2)
    else:
        avg_score_pct = 0

    # Best performance
    best_score_pct = 0
    best_quiz_title = 'N/A'
    if all_results:
        best_result = max(all_results, key=lambda x: (x['score'] / x['total_questions']) if x['total_questions'] > 0 else 0)
        best_score_pct = round((best_result['score'] / best_result['total_questions'] * 100) if best_result['total_questions'] > 0 else 0, 2)
        best_quiz_title = best_result['title']

    # Quiz-by-quiz performance
    quiz_performance = []
    quiz_stats = {}
    for result in all_results:
        quiz_id = result['quiz_id']
        if quiz_id not in quiz_stats:
            quiz_stats[quiz_id] = {
                'title': result['title'],
                'attempts': 0,
                'scores': [],
                'dates': []
            }
        quiz_stats[quiz_id]['attempts'] += 1
        score_pct = round((result['score'] / result['total_questions'] * 100) if result['total_questions'] > 0 else 0, 2)
        quiz_stats[quiz_id]['scores'].append(score_pct)
        quiz_stats[quiz_id]['dates'].append(result['completed_at'])

    for quiz_id, stats in quiz_stats.items():
        quiz_performance.append({
            'title': stats['title'],
            'attempts': stats['attempts'],
            'best_score': max(stats['scores']) if stats['scores'] else 0,
            'avg_score': round(sum(stats['scores']) / len(stats['scores']), 2) if stats['scores'] else 0,
            'last_attempted': stats['dates'][0].strftime('%Y-%m-%d') if stats['dates'] else 'N/A'
        })

    # Sort by attempts (most recent first by date within same attempt count)
    quiz_performance.sort(key=lambda x: x['last_attempted'], reverse=True)

    # Performance over time (last 10 attempts)
    recent_attempts = sorted(all_results, key=lambda x: x['completed_at'])[-10:]
    performance_data = {
        'labels': [r['completed_at'].strftime('%m-%d %H:%M') if hasattr(r['completed_at'], 'strftime') else str(r['completed_at']) for r in recent_attempts],
        'scores': [round((r['score'] / r['total_questions'] * 100) if r['total_questions'] > 0 else 0, 2) for r in recent_attempts]
    }

    # Score distribution (categorize all scores)
    score_counts = {'Excellent (80+)': 0, 'Good (60-79)': 0, 'Fair (40-59)': 0, 'Poor (<40)': 0}
    for result in all_results:
        score_pct = (result['score'] / result['total_questions'] * 100) if result['total_questions'] > 0 else 0
        if score_pct >= 80:
            score_counts['Excellent (80+)'] += 1
        elif score_pct >= 60:
            score_counts['Good (60-79)'] += 1
        elif score_pct >= 40:
            score_counts['Fair (40-59)'] += 1
        else:
            score_counts['Poor (<40)'] += 1

    distribution_data = {
        'labels': [k for k, v in score_counts.items() if v > 0] or ['No Data'],
        'values': [v for v in score_counts.values() if v > 0] or [0]
    }

    # Current streak (consecutive days with attempts, if any)
    current_streak = 0
    if all_results:
        sorted_dates = sorted(set([r['completed_at'].date() if hasattr(r['completed_at'], 'date') else r['completed_at'] for r in all_results]), reverse=True)
        from datetime import datetime, timedelta
        today = datetime.now().date()
        for i, date in enumerate(sorted_dates):
            expected_date = today - timedelta(days=i)
            if date == expected_date:
                current_streak += 1
            else:
                break

    conn.close()

    return render_template(
        'student_analytics.html',
        total_quizzes_attempted=len(quiz_stats),
        total_quizzes_available=total_quizzes_available,
        total_attempts=total_attempts,
        avg_score_pct=avg_score_pct,
        best_score_pct=best_score_pct,
        best_quiz_title=best_quiz_title,
        current_streak=current_streak,
        quiz_performance=quiz_performance,
        performance_data=performance_data,
        distribution_data=distribution_data
    )


@app.route('/student/dashboard')
@session_required(role='student')
def student_dashboard():
    
    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM quizzes")
    quizzes = c.fetchall()
    c.execute("SELECT * FROM results WHERE user_id = %s ORDER BY completed_at DESC", (session['user_id'],))
    results = c.fetchall()

    # Student metrics: average score percent across results (if any)
    c.execute("SELECT AVG(CAST(score AS FLOAT) / NULLIF(total_questions,0)) as avg_ratio FROM results WHERE user_id = %s", (session['user_id'],))
    avg_row = c.fetchone()
    avg_ratio = avg_row['avg_ratio'] if avg_row and avg_row['avg_ratio'] is not None else 0
    avg_percent = round(float(avg_ratio) * 100, 2) if avg_ratio else 0

    conn.close()
    
    return render_template('student_dashboard.html', quizzes=quizzes, results=results, avg_percent=avg_percent)

# -------------------- Student: Notifications --------------------
@app.route('/student/notifications')
@session_required(role='student')
def student_notifications():
    conn = get_db()
    c = conn.cursor(dictionary=True)
    
    # Fetch notifications (admin broadcast notifications)
    c.execute("SELECT * FROM notifications ORDER BY created_at DESC LIMIT 20")
    notifications = c.fetchall()
    conn.close()
    
    return render_template('student_notifications.html', notifications=notifications)

# -------------------- Admin: Analytics --------------------
@app.route('/admin/analytics')
@session_required(role='admin')
def admin_analytics():

    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT COUNT(*) as total_students FROM users WHERE role='student'")
    total_students = c.fetchone()['total_students']
    c.execute("SELECT COUNT(*) as total_lecturers FROM users WHERE role='lecturer'")
    total_lecturers = c.fetchone()['total_lecturers']
    c.execute("SELECT COUNT(*) as total_quizzes FROM quizzes")
    total_quizzes = c.fetchone()['total_quizzes']
    c.execute("SELECT AVG(CAST(score AS FLOAT) / NULLIF(total_questions,0)) as avg_ratio FROM results")
    avg_row = c.fetchone()
    avg_ratio = avg_row['avg_ratio'] if avg_row and avg_row['avg_ratio'] is not None else 0
    avg_score_pct = round(float(avg_ratio) * 100, 2) if avg_ratio else 0
    conn.close()
    
    stats = {
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_quizzes': total_quizzes,
        'avg_score_pct': avg_score_pct
    }
    
    return render_template('admin_analytics.html', stats=stats)


@app.route('/analytics')
@session_required()
def analytics():

    conn = get_db()
    c = conn.cursor(dictionary=True)

    # Basic stats
    c.execute("SELECT COUNT(*) as total_students FROM users WHERE role='student'")
    total_students = c.fetchone()['total_students']
    c.execute("SELECT COUNT(*) as total_lecturers FROM users WHERE role='lecturer'")
    total_lecturers = c.fetchone()['total_lecturers']
    c.execute("SELECT COUNT(*) as total_quizzes FROM quizzes")
    total_quizzes = c.fetchone()['total_quizzes']
    c.execute("SELECT AVG(CAST(score AS FLOAT) / NULLIF(total_questions,0)) as avg_ratio FROM results")
    avg_row = c.fetchone()
    avg_ratio = avg_row['avg_ratio'] if avg_row and avg_row['avg_ratio'] is not None else 0
    avg_score_pct = round(float(avg_ratio) * 100, 2) if avg_ratio else 0

    # Monthly stats (last 6 months)
    c.execute("SELECT DATE_FORMAT(completed_at, '%Y-%m') as month, COUNT(DISTINCT user_id) as unique_students, COUNT(*) as total_attempts FROM results WHERE completed_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) GROUP BY month ORDER BY month")
    monthly_rows = c.fetchall()
    monthly_labels = [r['month'] for r in monthly_rows]
    monthly_unique_students = [r['unique_students'] for r in monthly_rows]
    monthly_total_attempts = [r['total_attempts'] for r in monthly_rows]

    # Top quizzes
    c.execute("SELECT q.title, COUNT(r.id) as attempts, AVG(CAST(r.score AS FLOAT)/NULLIF(r.total_questions,0))*100 as avg_score FROM quizzes q LEFT JOIN results r ON q.id = r.quiz_id GROUP BY q.id ORDER BY attempts DESC LIMIT 6")
    top_rows = c.fetchall()
    quiz_labels = [r['title'] for r in top_rows]
    quiz_attempts = [r['attempts'] or 0 for r in top_rows]
    quiz_avg_scores = [round(r['avg_score'] or 0,2) for r in top_rows]

    # Recent user activity (last 7 days)
    c.execute("SELECT DATE(completed_at) as date, COUNT(DISTINCT user_id) as active_students, COUNT(*) as quiz_attempts FROM results WHERE completed_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY DATE(completed_at) ORDER BY DATE(completed_at) DESC")
    activity_rows = c.fetchall()
    user_activity = []
    for r in activity_rows:
        user_activity.append({
            'date': r['date'],
            'active_students': r['active_students'],
            'quiz_attempts': r['quiz_attempts']
        })

    conn.close()

    stats = {
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_quizzes': total_quizzes,
        'avg_score_pct': avg_score_pct
    }

    return render_template('AnalyticsDashboard.html',
                           stats=stats,
                           monthly_labels=monthly_labels,
                           monthly_unique_students=monthly_unique_students,
                           monthly_total_attempts=monthly_total_attempts,
                           quiz_labels=quiz_labels,
                           quiz_attempts=quiz_attempts,
                           quiz_avg_scores=quiz_avg_scores,
                           user_activity=user_activity)

# app.py (New / Modified Routes)

@app.route('/student/quiz/<int:quiz_id>')
@session_required(role='student')
def take_quiz(quiz_id):
    conn = get_db()
    if not conn:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('student_dashboard'))
    
    c = conn.cursor(dictionary=True)
    
    # 1. Fetch Quiz Info
    c.execute("SELECT * FROM quizzes WHERE id = %s", (quiz_id,))
    quiz = c.fetchone()
    if not quiz:
        flash('Quiz not found.', 'error')
        conn.close()
        return redirect(url_for('student_dashboard'))
    
    # 2. Get ALL question IDs for the quiz (to be managed dynamically)
    # We will fetch a list of all IDs, sorted by a weighted random order,
    # prioritizing a mix of difficulties for the initial set.
    c.execute("""
        SELECT id, difficulty_level 
        FROM questions 
        WHERE quiz_id = %s 
        ORDER BY FIELD(difficulty_level, 'Medium', 'Easy', 'Hard'), RAND()
    """, (quiz_id,))
    all_question_data = c.fetchall()
    conn.close()

    if not all_question_data:
        flash('This quiz has no questions.', 'error')
        return redirect(url_for('student_dashboard'))

    # Store necessary quiz state in the session
    session[f'quiz_state_{quiz_id}'] = {
        'question_ids': [q['id'] for q in all_question_data], # Full list of IDs
        'current_index': 0,           # Index of the next question to ask
        'answers': {},                # Stores user's answers and time taken
        'score': 0,
        'start_time': datetime.now().isoformat(),
        'total_questions': len(all_question_data)
    }

    # Redirect to the first question
    return redirect(url_for('serve_question', quiz_id=quiz_id))
# app.py (New / Modified Routes)

@app.route('/student/quiz/<int:quiz_id>/question')
@session_required(role='student')
def serve_question(quiz_id):
    state_key = f'quiz_state_{quiz_id}'
    quiz_state = session.get(state_key)
    # Debug info
    print(f"[DEBUG] serve_question: quiz_state={quiz_state}")
    if not quiz_state:
        flash('Quiz session not found or expired.', 'error')
        return redirect(url_for('student_dashboard'))

    current_index = quiz_state.get('current_index', 0)
    question_ids = quiz_state.get('question_ids', [])
    print(f"[DEBUG] serve_question: current_index={current_index}, question_ids={question_ids}")
    # Check if the quiz is finished
    if current_index >= len(question_ids):
        # Quiz is complete, submit results
        print(f"[DEBUG] serve_question: quiz finished, redirecting to submit_quiz")
        return redirect(url_for('submit_quiz', quiz_id=quiz_id))

    current_question_id = question_ids[current_index]
    conn = get_db()
    if not conn:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('student_dashboard'))
    c = conn.cursor(dictionary=True)
    # Fetch current question details
    c.execute("SELECT * FROM questions WHERE id = %s", (current_question_id,))
    question = c.fetchone()
    c.execute("SELECT id, title, description, duration FROM quizzes WHERE id = %s", (quiz_id,))
    quiz = c.fetchone()
    conn.close()
    # Start time for this specific question
    quiz_state['question_start_time'] = datetime.now().isoformat()
    session[state_key] = quiz_state # Update session
    # Pass only the current question as a list
    if not question:
        flash('Question not found.', 'error')
        return redirect(url_for('student_dashboard'))
    # Ensure question contains an id
    if 'id' not in question:
        flash('Invalid question format.', 'error')
        return redirect(url_for('student_dashboard'))
    print(f"[DEBUG] serve_question: rendering question {question['id']}")
    return render_template('take_quiz.html', 
                           quiz=quiz, 
                           questions=[question],
                           current_question_number=current_index + 1,
                           total_questions=20)

@app.route('/student/submit-quiz/<int:quiz_id>', methods=['POST'])
@session_required(role='student')
def submit_quiz(quiz_id):
    state_key = f'quiz_state_{quiz_id}'
    quiz_state = session.get(state_key)
    
    if not quiz_state:
        # If no quiz state, this POST is likely from a manual end, proceed to final submission
        flash('Quiz session expired. Please start the quiz again.', 'error')
        return redirect(url_for('student_dashboard'))

    current_index = quiz_state['current_index']
    question_ids = quiz_state['question_ids']
    
    # --- Check if user clicked "End Quiz" button ---
    end_quiz_clicked = request.form.get('end_quiz') == 'true'
    
    if end_quiz_clicked:
        # User wants to end the quiz now, finalize immediately
        total_questions = quiz_state['total_questions']
        score = quiz_state['score']
        conn = get_db()
        if not conn:
            flash('Database connection error. Could not submit quiz results.', 'error')
            return redirect(url_for('student_dashboard'))
        try:
            c = conn.cursor()
            c.execute("INSERT INTO results (user_id, quiz_id, score, total_questions) VALUES (%s, %s, %s, %s)",
                      (session['user_id'], quiz_id, score, total_questions))
            conn.commit()
            result_id = c.lastrowid
            flash(f"Quiz ended! Your final score: {score}/{total_questions}", 'success')
        except Exception as e:
            flash(f"[ERROR] Failed to insert results: {e}", 'error')
            result_id = None
        finally:
            c.close()
            conn.close()
        session.pop(state_key, None)
        
        # Redirect to result details page if result was saved successfully
        if result_id:
            return redirect(url_for('view_result', result_id=result_id))
        else:
            return redirect(url_for('student_dashboard'))
    
    # --- Always process the current question ---
    if 'question_start_time' in quiz_state:
        current_question_id = question_ids[current_index]
        user_answer = request.form.get(f"question_{current_question_id}")
        print(f"[DEBUG] Form data: {request.form}")
        print(f"[DEBUG] current_question_id={current_question_id}, user_answer={user_answer}")
        start_time = datetime.fromisoformat(quiz_state.pop('question_start_time'))
        time_taken = (datetime.now() - start_time).total_seconds()
        conn = get_db()
        if not conn:
            flash('Database connection error. Please try again.', 'error')
            return redirect(url_for('student_dashboard'))
        c = conn.cursor(dictionary=True)
        c.execute("SELECT correct_answer, difficulty_level FROM questions WHERE id = %s", (current_question_id,))
        question_data = c.fetchone()
        print(f"[DEBUG] question_data={question_data}")
        conn.close()
        # Normalize answers for comparison: strip whitespace and convert to uppercase
        user_answer_normalized = user_answer.strip().upper() if user_answer else None
        correct_answer_normalized = question_data['correct_answer'].strip().upper() if question_data and question_data['correct_answer'] else None
        is_correct = (user_answer_normalized == correct_answer_normalized) if user_answer_normalized and correct_answer_normalized else False
        print(f"[DEBUG] is_correct={is_correct}, user_answer_normalized={user_answer_normalized}, correct_answer_normalized={correct_answer_normalized}")
        quiz_state['answers'][str(current_question_id)] = {
            'answer': user_answer,
            'is_correct': is_correct,
            'time_taken': time_taken,
            'difficulty': question_data['difficulty_level'] if question_data else 'Unknown'
        }
        if is_correct:
            quiz_state['score'] += 1
            flash(f"Correct answer! ({current_index + 1}/{20})", 'success')
        else:
            flash(f"Incorrect answer. ({current_index + 1}/{20})", 'error')
        # Always increment by 1 for next question
        quiz_state['current_index'] += 1
        session[state_key] = quiz_state
        # If quiz is finished, finalize
        if quiz_state['current_index'] >= 20:
            total_questions = 20
            score = quiz_state['score']
            conn = get_db()
            if not conn:
                flash('Database connection error. Could not submit quiz results.', 'error')
                return redirect(url_for('student_dashboard'))
            try:
                c = conn.cursor()
                c.execute("INSERT INTO results (user_id, quiz_id, score, total_questions) VALUES (%s, %s, %s, %s)",
                          (session['user_id'], quiz_id, score, total_questions))
                conn.commit()
                result_id = c.lastrowid
                flash(f'Quiz submitted! Your final score: {score}/{total_questions}', 'success')
            except Exception as e:
                flash(f"[ERROR] Failed to insert results: {e}", 'error')
                result_id = None
            finally:
                c.close()
                conn.close()
            session.pop(state_key, None)
            
            # Redirect to result details page if result was saved successfully
            if result_id:
                return redirect(url_for('view_result', result_id=result_id))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash(f"Next question index: {quiz_state['current_index']}", 'info')
            return redirect(url_for('serve_question', quiz_id=quiz_id))

    # --- FINAL SUBMISSION (The quiz is officially over) ---
    # (Handled above, no need for duplicate logic)
# ==================== STUDENT: VIEW RESULT DETAILS ====================
@app.route('/student/result/<int:result_id>')
@session_required(role='student')
def view_result(result_id):
    conn = get_db()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('student_dashboard'))
    c = conn.cursor(dictionary=True)
    c.execute("SELECT r.*, q.title FROM results r JOIN quizzes q ON r.quiz_id = q.id WHERE r.id = %s AND r.user_id = %s", (result_id, session['user_id']))
    result = c.fetchone()
    conn.close()
    if not result:
        flash('Result not found or access denied.', 'error')
        return redirect(url_for('student_dashboard'))
    return render_template('result_details.html', result=result)
if __name__ == '__main__':
    app.run(debug=True, port=5000)

