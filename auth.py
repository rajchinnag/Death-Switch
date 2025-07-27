
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import sqlite3
import hashlib

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        if password != confirm:
            flash("Passwords do not match")
            return redirect('/register')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already exists")
            return redirect('/register')
        conn.close()
        flash("Registered successfully")
        return redirect('/login')
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password_hash)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
