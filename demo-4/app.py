#!/usr/bin/env python3
"""
LoveRoute - Romantic Travel Route Planner for Russia
A Flask-based web application featuring Tinder-style swiping for romantic locations

Author: Developer
Version: 1.0
License: MIT
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
import json
import os
import hashlib
import secrets
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Database initialization
def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('love_route.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            city TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User swipes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS swipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            place_id TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User routes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            route_name TEXT NOT NULL,
            places TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_cities():
    """Load cities data from JSON file"""
    try:
        with open('data/cities.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {"id": "msk", "name": "Москва"},
            {"id": "spb", "name": "Санкт-Петербург"},
            {"id": "nsk", "name": "Новосибирск"},
            {"id": "ekb", "name": "Екатеринбург"},
            {"id": "kzn", "name": "Казань"}
        ]

def load_places():
    """Load places data from JSON file"""
    try:
        with open('data/places.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_user_swipes(user_id):
    """Get all swipes for a user"""
    conn = sqlite3.connect('love_route.db')
    cursor = conn.cursor()
    cursor.execute('SELECT place_id, action FROM swipes WHERE user_id = ?', (user_id,))
    swipes = cursor.fetchall()
    conn.close()
    return {place_id: action for place_id, action in swipes}

@app.route('/')
def index():
    """Main landing page"""
    if 'user_id' in session:
        return redirect(url_for('swipe'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        city = request.form.get('city')
        
        if not email or not password or not city:
            flash('Все поля обязательны для заполнения', 'error')
            return render_template('register.html', cities=load_cities())
        
        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return render_template('register.html', cities=load_cities())
        
        conn = sqlite3.connect('love_route.db')
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash('Пользователь с таким email уже существует', 'error')
            conn.close()
            return render_template('register.html', cities=load_cities())
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        
        try:
            cursor.execute(
                'INSERT INTO users (id, email, password_hash, city) VALUES (?, ?, ?, ?)',
                (user_id, email, password_hash, city)
            )
            conn.commit()
            session['user_id'] = user_id
            session['user_city'] = city
            flash('Регистрация успешна! Добро пожаловать!', 'success')
            return redirect(url_for('swipe'))
        except Exception as e:
            flash('Ошибка регистрации. Попробуйте позже.', 'error')
        finally:
            conn.close()
    
    return render_template('register.html', cities=load_cities())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email и пароль обязательны', 'error')
            return render_template('login.html')
        
        conn = sqlite3.connect('love_route.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash, city FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[1] == hash_password(password):
            session['user_id'] = user[0]
            session['user_city'] = user[2]
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('swipe'))
        else:
            flash('Неверный email или пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/swipe')
def swipe():
    """Main swipe interface"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_city = session.get('user_city', 'msk')
    places = load_places()
    city_places = [p for p in places if p['cityId'] == user_city]
    
    # Get user's previous swipes
    user_swipes = get_user_swipes(session['user_id'])
    
    # Filter out already swiped places
    available_places = [p for p in city_places if p['id'] not in user_swipes]
    
    return render_template('swipe.html', 
                         places=available_places, 
                         city=user_city,
                         total_places=len(city_places),
                         swiped_count=len(user_swipes))

@app.route('/api/swipe', methods=['POST'])
def api_swipe():
    """Handle swipe actions"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    place_id = data.get('place_id')
    action = data.get('action')  # 'like' or 'skip'
    
    if not place_id or action not in ['like', 'skip']:
        return jsonify({'error': 'Invalid data'}), 400
    
    conn = sqlite3.connect('love_route.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO swipes (user_id, place_id, action) VALUES (?, ?, ?)',
            (session['user_id'], place_id, action)
        )
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/liked-places')
def api_liked_places():
    """Get user's liked places"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('love_route.db')
    cursor = conn.cursor()
    cursor.execute('SELECT place_id FROM swipes WHERE user_id = ? AND action = "like"', 
                   (session['user_id'],))
    liked_place_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    places = load_places()
    liked_places = [p for p in places if p['id'] in liked_place_ids]
    
    return jsonify(liked_places)

@app.route('/routes')
def routes():
    """User's saved routes"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('love_route.db')
    cursor = conn.cursor()
    cursor.execute('SELECT route_name, places, created_at FROM routes WHERE user_id = ?', 
                   (session['user_id'],))
    user_routes = cursor.fetchall()
    conn.close()
    
    # Parse routes data
    routes_data = []
    for route in user_routes:
        route_places = json.loads(route[1])
        routes_data.append({
            'name': route[0],
            'places': route_places,
            'created_at': route[2],
            'count': len(route_places)
        })
    
    return render_template('routes.html', routes=routes_data)

@app.route('/api/cities')
def api_cities():
    """API endpoint for cities"""
    return jsonify(load_cities())

@app.route('/api/places')
def api_places():
    """API endpoint for places"""
    city = request.args.get('city', 'msk')
    places = load_places()
    city_places = [p for p in places if p['cityId'] == city]
    return jsonify(city_places)

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)