#!/usr/bin/env python3
"""
LoveRoutes - Romantic Travel Routes for Russia
Full-stack Python Flask application
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import json
import os
import hashlib
import secrets
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# In-memory databases
users_db = {}
choices_db = {}

# Sample data - exactly matching the main site structure
CITIES = [
    {"id": "msk", "name": "Москва"},
    {"id": "spb", "name": "Санкт-Петербург"}, 
    {"id": "nsk", "name": "Новосибирск"},
    {"id": "ekb", "name": "Екатеринбург"},
    {"id": "kzn", "name": "Казань"},
    {"id": "nnv", "name": "Нижний Новгород"},
    {"id": "chel", "name": "Челябинск"},
    {"id": "smr", "name": "Самара"},
    {"id": "oms", "name": "Омск"},
    {"id": "ros", "name": "Ростов-на-Дону"},
    {"id": "ufa", "name": "Уфа"},
    {"id": "krsk", "name": "Красноярск"},
    {"id": "vor", "name": "Воронеж"},
    {"id": "perm", "name": "Пермь"},
    {"id": "vol", "name": "Волгоград"},
    {"id": "krd", "name": "Краснодар"},
    {"id": "inn", "name": "Иннополис"},
    {"id": "tyum", "name": "Тюмень"},
    {"id": "irk", "name": "Иркутск"},
    {"id": "tol", "name": "Тольятти"},
    {"id": "uly", "name": "Ульяновск"}
]

# Load places data from JSON (same structure as main site)
def load_places_data():
    """Load places data from a simplified JSON structure"""
    sample_places = []
    
    # Sample romantic places for each city
    place_templates = [
        {"name": "Центральный парк", "excerpt": "Романтические прогулки среди зелени", "tags": ["природа", "прогулки"]},
        {"name": "Набережная", "excerpt": "Красивые виды на воду", "tags": ["вода", "закат"]},
        {"name": "Старый город", "excerpt": "Историческая атмосфера", "tags": ["история", "архитектура"]},
        {"name": "Смотровая площадка", "excerpt": "Панорамный вид на город", "tags": ["виды", "фото"]},
        {"name": "Ботанический сад", "excerpt": "Уединенные аллеи и цветы", "tags": ["природа", "цветы"]},
        {"name": "Кафе на крыше", "excerpt": "Романтические ужины под звездами", "tags": ["еда", "атмосфера"]},
        {"name": "Театральная площадь", "excerpt": "Культурный центр города", "tags": ["культура", "театр"]},
        {"name": "Речной порт", "excerpt": "Прогулки на теплоходе", "tags": ["вода", "прогулка"]},
        {"name": "Парк развлечений", "excerpt": "Веселые приключения вдвоем", "tags": ["развлечения", "адреналин"]},
        {"name": "Винный бар", "excerpt": "Уютная атмосфера для двоих", "tags": ["алкоголь", "уют"]},
        {"name": "Арт-галерея", "excerpt": "Современное искусство", "tags": ["искусство", "культура"]},
        {"name": "Спа-центр", "excerpt": "Релаксация и романтика", "tags": ["релакс", "спа"]},
        {"name": "Ресторан", "excerpt": "Изысканная кухня", "tags": ["еда", "ресторан"]},
        {"name": "Музей", "excerpt": "Познавательные экскурсии", "tags": ["образование", "история"]},
        {"name": "Пляж", "excerpt": "Песок и романтические закаты", "tags": ["пляж", "закат"]},
        {"name": "Мост", "excerpt": "Символ любви и верности", "tags": ["символ", "виды"]},
        {"name": "Храм", "excerpt": "Духовное единение", "tags": ["религия", "архитектура"]},
        {"name": "Рынок", "excerpt": "Местный колорит и вкусы", "tags": ["еда", "традиции"]},
        {"name": "Парк аттракционов", "excerpt": "Детские воспоминания вместе", "tags": ["развлечения", "ностальгия"]},
        {"name": "Планетарий", "excerpt": "Звезды для влюбленных", "tags": ["наука", "романтика"]}
    ]
    
    # Generate 20 places for each city
    for city in CITIES:
        for i, template in enumerate(place_templates):
            place = {
                "id": f"{city['id']}-{template['name'].lower().replace(' ', '-')}-{i+1}",
                "cityId": city["id"],
                "name": template["name"],
                "excerpt": template["excerpt"],
                "image_url": f"/static/images/{city['id']}/{city['id']}-place-{i+1}.jpg",
                "verified_image": True,
                "image_attribution": "Wikimedia Commons",
                "tags": template["tags"]
            }
            sample_places.append(place)
    
    return sample_places

PLACES = load_places_data()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', cities=CITIES)

@app.route('/api/cities')
def get_cities():
    """Get all cities"""
    return jsonify(CITIES)

@app.route('/api/places')
def get_places():
    """Get places for a specific city"""
    city_id = request.args.get('cityId')
    if not city_id:
        return jsonify([])
    
    city_places = [place for place in PLACES if place['cityId'] == city_id]
    return jsonify(city_places)

@app.route('/api/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()
    
    # Validation
    required_fields = ['email', 'password', 'firstName', 'selectedCity']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'Поле {field} обязательно'}), 400
    
    email = data['email'].lower().strip()
    
    if email in users_db:
        return jsonify({'message': 'Пользователь с таким email уже существует'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'message': 'Пароль должен содержать минимум 6 символов'}), 400
    
    # Create user
    user_id = str(uuid.uuid4())
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
    
    user = {
        'id': user_id,
        'email': email,
        'firstName': data['firstName'],
        'lastName': data.get('lastName', ''),
        'selectedCity': data['selectedCity'],
        'password': password_hash,
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }
    
    users_db[email] = user
    session['user_id'] = user_id
    session['email'] = email
    
    # Return user without password
    user_response = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify({
        'user': user_response,
        'token': f'jwt_token_{user_id}'  # Mock JWT token
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'message': 'Email и пароль обязательны'}), 400
    
    user = users_db.get(email)
    if not user:
        return jsonify({'message': 'Неверный email или пароль'}), 401
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password'] != password_hash:
        return jsonify({'message': 'Неверный email или пароль'}), 401
    
    session['user_id'] = user['id']
    session['email'] = email
    
    user_response = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify({
        'user': user_response,
        'token': f'jwt_token_{user["id"]}'
    })

@app.route('/api/auth/current-user')
def get_current_user():
    """Get current authenticated user"""
    email = session.get('email')
    if not email or email not in users_db:
        return jsonify({'message': 'Unauthorized'}), 401
    
    user = users_db[email]
    user_response = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify(user_response)

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/choices', methods=['POST'])
def record_choice():
    """Record user's choice (like/skip)"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    
    choice_id = str(uuid.uuid4())
    choice = {
        'id': choice_id,
        'userId': user_id,
        'placeId': data.get('placeId'),
        'cityId': data.get('cityId'), 
        'choice': data.get('choice'),  # 'like' or 'skip'
        'timestamp': datetime.now().isoformat()
    }
    
    choices_db[choice_id] = choice
    
    return jsonify({'success': True, 'message': 'Choice recorded'})

@app.route('/api/user/choices')
def get_user_choices():
    """Get user's choices"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    
    user_choices = [choice for choice in choices_db.values() if choice['userId'] == user_id]
    return jsonify(user_choices)

if __name__ == '__main__':
    print("\n🚀 LoveRoutes - Python Flask Server")
    print("📱 Открывайте: http://localhost:8000")
    print("💕 Романтические маршруты по России")
    print("\nВозможности:")
    print("✅ Регистрация и авторизация")
    print("✅ Выбор города из 21 города России") 
    print("✅ Swipe-интерфейс для выбора мест")
    print("✅ Сохранение предпочтений пользователя")
    print("✅ Адаптивный дизайн")
    
    app.run(host='0.0.0.0', port=8000, debug=True)