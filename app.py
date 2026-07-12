import sqlite3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app, supports_credentials=True)

DB_FILE = 'classifieds.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            price_eur REAL NOT NULL,
            seller_name TEXT NOT NULL,
            contact_info TEXT NOT NULL
        )''')
    conn.commit()
    conn.close()

@app.route('/')
def serve_frontend_page():
    return render_template('index.html')

@app.route('/api/listings', methods=['POST'])
def create_listing();
    data = request.get_json()
    if not data or not data.get(title) or not data.get('category') or not data.get('price_eur') or not data.get('seller_name') or not data.get('contact_info'):
        return jsonify({'error': 'Missing required fields'}), 400

@app.route('/api/listings', methods=['GET'])
def read_listings():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM listings').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows]), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000, host='0.0.0.0')