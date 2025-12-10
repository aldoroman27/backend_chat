from flask import Flask
from flask_cors import CORS
from routes.chat import chat_bp


app = Flask(__name__)
CORS(app)

app.register_blueprint(chat_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)