#!/usr/bin/env python3
"""
LoveRoute - Романтический маршрутный планировщик для России
Tinder-стиль свайпинг для выбора романтических мест
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  city TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_swipes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  place_id TEXT,
                  action TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

# Загрузка данных
def load_cities():
    with open('data/cities.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_places():
    with open('data/places.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_places_for_city(city_id):
    places = load_places()
    return [p for p in places if p['cityId'] == city_id]

# Аутентификация
def create_user(email, password, city):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        c.execute("INSERT INTO users (email, password_hash, city) VALUES (?, ?, ?)",
                 (email, password_hash, city))
        user_id = c.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, password_hash, city FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        return {'id': user[0], 'email': email, 'city': user[2]}
    return None

def get_user_swipes(user_id, city_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT place_id, action FROM user_swipes WHERE user_id = ?", (user_id,))
    swipes = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return swipes

def save_swipe(user_id, place_id, action):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_swipes (user_id, place_id, action) VALUES (?, ?, ?)",
             (user_id, place_id, action))
    conn.commit()
    conn.close()

# Маршруты
@app.route('/')
def index():
    if 'user_id' not in session:
        return render_template('landing.html')
    
    # Пользователь вошел - показываем главную страницу
    city_id = session.get('city_id') or request.args.get('city')
    if not city_id:
        cities = load_cities()
        return render_template('city_select.html', cities=cities)
    
    session['city_id'] = city_id
    places = get_places_for_city(city_id)
    user_swipes = get_user_swipes(session['user_id'], city_id)
    
    # Фильтруем места которые еще не свайпнули
    unswiped = [p for p in places if p['id'] not in user_swipes]
    
    cities = load_cities()
    current_city = next((c for c in cities if c['id'] == city_id), None)
    
    return render_template('swipe.html', 
                         places=unswiped, 
                         city=current_city,
                         user_email=session.get('email'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['city_id'] = user['city']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверный email или пароль")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        city = request.form['city']
        
        if len(password) < 6:
            cities = load_cities()
            return render_template('register.html', cities=cities, 
                                 error="Пароль должен содержать минимум 6 символов")
        
        user_id = create_user(email, password, city)
        if user_id:
            session['user_id'] = user_id
            session['email'] = email
            session['city_id'] = city
            return redirect(url_for('index'))
        else:
            cities = load_cities()
            return render_template('register.html', cities=cities, 
                                 error="Пользователь с таким email уже существует")
    
    cities = load_cities()
    return render_template('register.html', cities=cities)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/swipe', methods=['POST'])
def api_swipe():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    place_id = data.get('place_id')
    action = data.get('action')  # 'like' или 'skip'
    
    if not place_id or action not in ['like', 'skip']:
        return jsonify({'error': 'Invalid data'}), 400
    
    save_swipe(session['user_id'], place_id, action)
    return jsonify({'success': True})

@app.route('/api/places')
def api_places():
    city_id = request.args.get('city')
    if not city_id:
        return jsonify({'error': 'City required'}), 400
    
    places = get_places_for_city(city_id)
    
    # Если пользователь вошел, фильтруем по свайпам
    if 'user_id' in session:
        user_swipes = get_user_swipes(session['user_id'], city_id)
        places = [p for p in places if p['id'] not in user_swipes]
    
    return jsonify(places)

@app.route('/api/cities')
def api_cities():
    cities = load_cities()
    return jsonify(cities)

@app.route('/guest')
def guest_mode():
    # Гостевой режим без регистрации
    city_id = request.args.get('city')
    if not city_id:
        cities = load_cities()
        return render_template('city_select.html', cities=cities, guest=True)
    
    places = get_places_for_city(city_id)
    cities = load_cities()
    current_city = next((c for c in cities if c['id'] == city_id), None)
    
    return render_template('swipe.html', 
                         places=places, 
                         city=current_city,
                         guest=True)

if __name__ == '__main__':
    # Создаем директории если их нет
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Инициализируем базу данных
    init_db()
    
    print("🚀 LoveRoute запущен на http://localhost:5000")
    print("💕 Романтические места России ждут вас!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)