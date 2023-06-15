from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import db, create_app
from datetime import datetime, date, time

class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200), unique=False)
    department = db.Column(db.String(50), unique=False)
    permission = db.Column(db.String(20), unique=False)

    def __init__(self, username, email, password, department):
        self.username = username
        self.email = email
        self.password = password
        self.department = department

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self): # line 37
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username
    
    def __repr__(self):
        return '%r' % self.username
    
class Visitor(db.Model):
    __tablename__ = "Visitor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False)
    department = db.Column(db.String(30), unique=False)
    phone = db.Column(db.String(30), unique=False)
    manager = db.Column(db.String(30), unique=False)
    device = db.Column(db.String(50), unique=False, nullable=True)
    serial_number = db.Column(db.String(50), unique=False, nullable=True)
    object = db.Column(db.String(50), unique=False)
    created_date = db.Column(db.DateTime, unique=False)
    exit_date = db.Column(db.DateTime, unique=False, nullable=True)
    exit = db.Column(db.Boolean(), unique=False, nullable=True)
    approve = db.Column(db.Boolean(), unique=False)

    def __init__(self, name, department, phone, manager, device, serial_number, object, created_time, approve):
        self.name = name
        self.department = department
        self.phone = phone
        self.manager = manager
        self.device = device
        self.serial_number = serial_number
        self.approve = approve
        self.object = object
        self.created_date = created_time
