from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from db_connector import db_connector

db_user, db_password, db_host, db_port, db_name = db_connector()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = 'acjkehrjkawekvhjkawtejk'
    app.config['JSON_AS_ASCII'] = False
    # # Login
    # login_manager = LoginManager()
    # login_manager.init_app(app)
    # login_manager.login_view = 'login'
    # login_manager.login_message = u"로그인 후에 서비스를 이용해주세요."
    # login_manager.login_message_category = "info"

    # from app import User
    # @login_manager.user_loader
    # def load_user(id):
    #     return User.query.get(id)  # primary_key

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    return app