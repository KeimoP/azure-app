from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Replace with a real secret key in production

# Database connection function with environment variables
def get_db_connection():
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')}"
    )
    try:
        return pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        app.logger.error(f"Database connection failed: {e}")
        raise

# Routes
@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
    except pyodbc.Error as e:
        flash("Database connection error. Please try again later.")
        app.logger.error(f"Database connection error: {e}")
        return redirect(url_for('error_page'))  # Define an error page
    cursor = conn.cursor()
    cursor.execute('SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC')
    posts = cursor.fetchall()
    conn.close()
    
    return render_template('home.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['user_id'] = user.id
            return redirect(url_for('home'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except pyodbc.Error as e:
            app.logger.error(f"Database error: {e}")
            flash('A database error occurred. Please try again.')
        finally:
            if 'conn' in locals():
                conn.close()

    return render_template('register.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO posts (content, user_id, created_at) VALUES (?, ?, GETDATE())',
                  (content, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    student_info = {
        'name': 'Keimo',  # Replace with your name
        'class': 'IT-24',
        'interests': ['Programming', 'Web Development', 'Azure Cloud'],
        'project_name': "Keimo's Social Hub"
    }
    
    return render_template('profile.html', info=student_info)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)