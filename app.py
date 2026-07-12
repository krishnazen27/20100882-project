import sqlite3
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app, supports_credentials=True)

DB_FILE = 'classifieds.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def serve_frontend_page():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')