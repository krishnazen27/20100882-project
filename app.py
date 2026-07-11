from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route('/')
def serve_frontend_page():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')