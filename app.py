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
            contact_info TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available'                
        )''')
    conn.commit()
    conn.close()

@app.route('/')
def serve_frontend_page():
    return render_template('index.html')

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
    rows = conn.execute('SELECT * FROM listings').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows]), 200

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
    return jsonify({"message": "Listing deleted successfully!"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000, host='0.0.0.0')