from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User
from database import init_db

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.doctor import doctor_bp
from routes.patient import patient_bp
from routes.chatbot import chatbot_bp
from routes.appointments import appointments_bp
from routes.insurance import insurance_bp
from routes.emergency import emergency_bp
from routes.predict import predict_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(doctor_bp, url_prefix="/doctor")
    app.register_blueprint(patient_bp, url_prefix="/patient")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    app.register_blueprint(appointments_bp, url_prefix="/appointments")
    app.register_blueprint(insurance_bp, url_prefix="/insurance")
    app.register_blueprint(emergency_bp, url_prefix="/emergency")
    app.register_blueprint(predict_bp, url_prefix="/predict")

    @app.route("/")
    def index():
        return render_template("index.html")

    init_db(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
