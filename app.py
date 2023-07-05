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
    profile_image = db.Column(db.String(120), nullable=True)
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
    work = db.Column(db.Boolean(), unique=False)
    remarks = db.Column(db.String(50), unique=False, nullable=True)
    object = db.Column(db.String(50), unique=False)
    created_date = db.Column(db.DateTime, unique=False)
    approve_date = db.Column(db.DateTime, unique=False)
    exit_date = db.Column(db.DateTime, unique=False, nullable=True)
    exit = db.Column(db.Boolean(), unique=False, nullable=True)
    approve = db.Column(db.Boolean(), unique=False)
    location = db.Column(db.String(50), unique=False, nullable=True)
    detail_location = db.Column(db.String(50), unique=False, nullable=True)
    company_type = db.Column(db.String(50), unique=False, nullable=True)
    company = db.Column(db.String(50), unique=False, nullable=True)
    work_content = db.Column(db.String(200), unique=False, nullable=True)
    registry = db.Column(db.String(50), unique=False, nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    rack_id = db.Column(db.Integer, db.ForeignKey('Rack.id'))
    cards = db.relationship('Card', backref='visitor')
    rack_keys = db.relationship('Rack', backref='visitor_rack')

    # 이름, 부서, 번호, 작업위치, 담당자, 장비체크, 비고, 방문목적, 등록시간, 승인, 사전/현장, 작업체크, 회사종류, 회사이름, 작업내용
    def __init__(self, name, department, phone, location, manager, device, remarks, object, created_time, approve, registry, work, company_type, company, work_content, detail_location):
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
        self.work = work
        self.company_type = company_type
        self.company = company
        self.work_content = work_content
        self.detail_location = detail_location

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

class Rack(db.Model):
    __tablename__ = "Rack"

    id = db.Column(db.Integer, primary_key=True)
    key_type = db.Column(db.String(50), unique=False)
    key_num = db.Column(db.String(50), unique=False, nullable=True)
    key_status = db.Column(db.String(50), unique=False, nullable=True)
    visitors = db.relationship('Visitor', backref='rack')

    def __init__(self, key_type, key_num, key_status):
        self.key_type = key_type
        self.key_num = key_num
        self.key_status = key_status

class Privacy(db.Model):
    __tablename__ = "Privacy"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False)
    department = db.Column(db.String(30), unique=False)
    phone = db.Column(db.String(30), unique=False)
    birth = db.Column(db.String(50), unique=False)
    email = db.Column(db.String(30), unique=False, nullable=True)
    manager = db.Column(db.String(30), unique=False, nullable=False)
    device = db.Column(db.Boolean(), unique=False, nullable=True)
    work = db.Column(db.Boolean(), unique=False, nullable=True)
    remarks = db.Column(db.String(50), unique=False, nullable=True)
    object = db.Column(db.String(50), unique=False)
    location = db.Column(db.String(50), unique=False, nullable=True)
    detail_location = db.Column(db.String(50), unique=False, nullable=True)
    company_type = db.Column(db.String(50), unique=False, nullable=True)
    company = db.Column(db.String(50), unique=False, nullable=True)
    work_content = db.Column(db.String(200), unique=False, nullable=True)
    visit_date = db.Column(db.DateTime, unique=False)
    registry = db.Column(db.String(50), unique=False, nullable=True)

    def __init__(self, name, department, phone, birth, email, manager, device, work, remarks, object, location, detail_location, company_type, company, work_content, visit_date, registry):
        self.name = name
        self.department = department
        self.phone = phone
        self.birth = birth
        self.email = email
        self.manager = manager
        self.device = device
        self.work = work
        self.remarks = remarks
        self.object = object
        self.location = location
        self.detail_location = detail_location
        self.company_type = company_type
        self.company = company
        self.work_content = work_content
        self.visit_date = visit_date
        self.work = work
        self.registry = registry
    

