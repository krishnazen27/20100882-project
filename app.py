from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def serve_frontend_page():
    return "Hello, Classifieds!"

if __name__ == '__main__':
    # Starts the local development server
    app.run(debug=True, port=5000, host='0.0.0.0')