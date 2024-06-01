from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Allow all origins for CORS
    CORS(app)

    with app.app_context():
        from .controllers import sentiment_bp
        app.register_blueprint(sentiment_bp)

    return app
