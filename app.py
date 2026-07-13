import os
import sqlite3
import urllib.request
import json
import random
import string
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')
app.secret_key = 'super_secret_dev_key_for_session_management'
CORS(app, supports_credentials=True)

def generate_dcm_id():
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=5))
    return f"DCM-{suffix}"

def get_db_file():
    if app.config.get('TESTING'):
        return 'test_classifieds.db'
    return 'classifieds.db'

def get_db_connection():
    conn = sqlite3.connect(get_db_file())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            contact_info TEXT NOT NULL
        )''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dcm_id TEXT UNIQUE,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            price_eur REAL NOT NULL,
            seller_name TEXT NOT NULL,
            contact_info TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available',
            seller_id INTEGER,
            buyer_id INTEGER,
            FOREIGN KEY(seller_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY(buyer_id) REFERENCES users(id) ON DELETE SET NULL
        )''')
    conn.commit()
    conn.close()

def get_external_price_in_usd(amount_eur):
    try:
        url = "https://open.er-api.com/v6/latest/EUR"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode())
            usd_rate = data["rates"].get("USD", 1.10)
            return round(amount_eur * usd_rate, 2)
    except Exception as e:
        return round(amount_eur * 1.10, 2)

@app.route('/')
def route_buying_tab():
    """Serves the main catalog browser marketplace screen."""
    return render_template('buying.html', active_page='buying')

@app.route('/selling')
def route_selling_tab():
    """Serves the advertisement creation and management dashboard."""
    return render_template('selling.html', active_page='selling')

@app.route('/profile')
def route_profile_tab():
    """Serves the login, register, and active configuration profile data."""
    return render_template('login.html', active_page='profile')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('contact_info'):
        return jsonify({"error": "All fields are required"}), 400
    
    hashed_password = generate_password_hash(data['password'])
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password_hash, contact_info) VALUES (?, ?, ?)',
                     (data['username'], hashed_password, data['contact_info']))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Username already exists"}), 409
    conn.close()
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing credentials"}), 400
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], data['password']):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['contact_info'] = user['contact_info']
        return jsonify({
            "message": "Login successful",
            "user": {"id": user['id'], "username": user['username'], "contact_info": user['contact_info']}
        }), 200
        
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/auth/session', methods=['GET'])
def get_session():
    if 'user_id' in session:
        return jsonify({
            "logged_in": True,
            "user": {"id": session['user_id'], "username": session['username'], "contact_info": session['contact_info']}
        }), 200
    return jsonify({"logged_in": False}), 200

@app.route('/api/listings', methods=['POST'])
def create_listing():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required to post an ad"}), 401
        
    data = request.get_json()
    if not data or not data.get('title') or not data.get('price_eur'):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    custom_id = generate_dcm_id()
    
    cursor.execute(
        'INSERT INTO listings (dcm_id, title, category, price_eur, seller_name, contact_info, status, seller_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (custom_id, data['title'], data.get('category', 'General'), float(data['price_eur']), session['username'], session['contact_info'], 'Available', session['user_id'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_id, "dcm_id": custom_id, "message": "Ad listed successfully!"}), 201

@app.route('/api/listings', methods=['GET'])
def read_listings():
    conn = get_db_connection()
    search_query = request.args.get('search', '')
    if search_query:
        rows = conn.execute(
            'SELECT * FROM listings WHERE title LIKE ? OR category LIKE ? OR seller_name LIKE ? OR dcm_id LIKE ?',
            (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        rows = conn.execute('SELECT * FROM listings').fetchall()
    conn.close()
    
    listings_list = []
    for row in rows:
        item = dict(row)
        item['price_usd'] = get_external_price_in_usd(item['price_eur'])
        listings_list.append(item)
    return jsonify(listings_list), 200

@app.route('/api/listings/<int:item_id>', methods=['PUT'])
def update_listing(item_id):
    data = request.get_json()
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM listings WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({"error": "Listing not found"}), 404
        
    if data.get('status') != 'Sold' and ('user_id' not in session or item['seller_id'] != session['user_id']):
        conn.close()
        return jsonify({"error": "Unauthorized mutation matrix exception"}), 403
        
    buyer_id = item['buyer_id']
    if data.get('status') == 'Sold':
        buyer_id = session.get('user_id')

    conn.execute(
        'UPDATE listings SET title = ?, category = ?, price_eur = ?, status = ?, buyer_id = ? WHERE id = ?',
        (data['title'], data['category'], float(data['price_eur']), data['status'], buyer_id, item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Listing updated successfully!"}), 200

@app.route('/api/listings/<int:item_id>', methods=['DELETE'])
def delete_listing(item_id):
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
        
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM listings WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({"error": "Listing not found"}), 404
        
    if item['seller_id'] != session['user_id']:
        conn.close()
        return jsonify({"error": "You do not own this ad"}), 403
        
    conn.execute('DELETE FROM listings WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Listing removed permanently."}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000, host='0.0.0.0')