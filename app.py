import sqlite3
import urllib.request
import json
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
app.secret_key = 'super_secret_dev_key_for_session_management' 
CORS(app, supports_credentials=True)

DB_FILE = 'classifieds.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
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
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            price_eur REAL NOT NULL,
            seller_name TEXT NOT NULL,
            contact_info TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available'                
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
        # Exchange-rate API unreachable - fall back to a fixed approximate rate
        return round(amount_eur * 1.10, 2)

@app.route('/')
def serve_frontend_page():
    return render_template('index.html')

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
        # UNIQUE constraint on username violated
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
            "user": {
                "id": session['user_id'],
                "username": session['username'],
                "contact_info": session['contact_info']
            }
        }), 200
    return jsonify({"logged_in": False}), 200

@app.route('/api/listings', methods=['POST'])
def create_listing():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('price_eur'):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO listings (title, category, price_eur, seller_name, contact_info, status) VALUES (?, ?, ?, ?, ?, ?)',
        (data['title'], data.get('category', 'General'), float(data['price_eur']),
         data.get('seller_name', 'Anonymous'), data.get('contact_info', 'n/a'), 'Available')
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_id, "message": "Ad listed successfully!"}), 201

@app.route('/api/listings', methods=['GET'])
def read_listings():
    conn = get_db_connection()
    search_query = request.args.get('search', '')
    if search_query:
        rows = conn.execute(
            'SELECT * FROM listings WHERE title LIKE ? OR category LIKE ?',
            (f'%{search_query}%', f'%{search_query}%')
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

    conn.execute(
        'UPDATE listings SET title = ?, category = ?, price_eur = ?, status = ? WHERE id = ?',
        (data['title'], data['category'], float(data['price_eur']), data['status'], item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Listing updated successfully!"}), 200

@app.route('/api/listings/<int:item_id>', methods=['DELETE'])
def delete_listing(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM listings WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({"error": "Listing not found"}), 404

    conn.execute('DELETE FROM listings WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Listing removed permanently."}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000, host='0.0.0.0')