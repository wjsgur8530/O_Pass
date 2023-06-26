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
    rank = db.Column(db.String(20), unique=False)
    user_info_id = db.relationship('User_log', backref='user_log')

    def __init__(self, username, email, password, department, rank):
        self.username = username
        self.email = email
        self.password = password
        self.department = department
        self.rank = rank

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
    
class User_log(db.Model):
    __tablename__ = "User_log"

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(30), unique=False)
    login_timestamp = db.Column(db.DateTime, unique=False)
    logout_timestamp =  db.Column(db.DateTime, unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    def __init__(self, ip_address, login_timestamp, user_id):
        self.ip_address = ip_address
        self.login_timestamp = login_timestamp
        self.user_id = user_id

class Visitor(db.Model):
    __tablename__ = "Visitor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    department = db.Column(db.String(30), unique=False)
    phone = db.Column(db.String(30), unique=False, nullable=False)
    manager = db.Column(db.String(30), unique=False, nullable=False)
    device = db.Column(db.Boolean(), unique=False)
    remarks = db.Column(db.String(50), unique=False, nullable=True)
    object = db.Column(db.String(50), unique=False)
    created_date = db.Column(db.DateTime, unique=False)
    exit_date = db.Column(db.DateTime, unique=False, nullable=True)
    exit = db.Column(db.Boolean(), unique=False, nullable=True)
    approve = db.Column(db.Boolean(), unique=False)
    location = db.Column(db.String(50), unique=False, nullable=True)
    registry = db.Column(db.String(50), unique=False, nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))

    def __init__(self, name, department, phone, location, manager, device, remarks, object, created_time, approve, registry):
        self.name = name
        self.department = department
        self.phone = phone
        self.location = location
        self.manager = manager
        self.device = device
        self.remarks = remarks
        self.approve = approve
        self.object = object
        self.created_date = created_time
        self.registry = registry

class Card(db.Model):
    __tablename__ = "Card"

    id = db.Column(db.Integer, primary_key=True)
    card_type = db.Column(db.String(50), unique=False)
    card_num = db.Column(db.String(50), unique=False, nullable=True)
    card_status = db.Column(db.String(50), unique=False, nullable=True)
    visitors = db.relationship('Visitor', backref='card')

    def __init__(self, card_type, card_num, card_status):
        self.card_type = card_type
        self.card_num = card_num
        self.card_status = card_status

class Year(db.Model):
    __tablename__ = "Year"

    year = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class Month(db.Model):
    __tablename__ = "Month"

    year = db.Column(db.Integer, db.ForeignKey('Year.year'), primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.Index('ix_month_id', 'month'),
    )

class Day(db.Model):
    __tablename__ = "Day"

    year = db.Column(db.Integer, db.ForeignKey('Year.year'), primary_key=True)
    month = db.Column(db.Integer, db.ForeignKey('Month.month'), primary_key=True)
    day = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class Department(db.Model):
    __tablename__ = "Department"

    id = db.Column(db.Integer, primary_key=True)
    department_type = db.Column(db.String(50), unique=False)
    department_name = db.Column(db.String(50), unique=True)

    def __init__(self, department_type, department_name):
        self.department_type = department_type
        self.department_name = department_name