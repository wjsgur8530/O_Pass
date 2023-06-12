#!/usr/bin/env python
from flask import Flask, flash, session, url_for, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # Password Hash
from flask_bcrypt import Bcrypt
from app import User, Visitor
import jinja2.exceptions
from config import create_app, db
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager
from datetime import datetime, date, time
import qrcode
import requests

app = create_app()
bcrypt = Bcrypt(app)

@app.route('/')
@app.route('/index')
@login_required
def index():
    img = qrcode.make("안녕하세요")
    img.save("C:\\Users\\User\\Desktop\\flask_O_pass\\flask_O_Pass\\qr_code.png")
    print(img)
    return render_template('index.html')

@app.route('/<pagename>')
def admin(pagename):
    return render_template(pagename+'.html')

# 회원가입 페이지
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 폼으로부터 입력받은 데이터 가져오기
        username = request.form['username']
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']

        # 유효성 검사
        user = User.query.filter_by(email=email).first()
        if user:
            flash("이미 가입된 이메일입니다.")
        elif len(email) < 5 :
            flash("이메일은 5자 이상입니다.")
        elif len(username) < 2:
            flash("이름은 2자 이상입니다.")
        elif password1 != password2 :
            flash("비밀번호와 비밀번호재입력이 서로 다릅니다.")
        elif len(password1) < 7:
            flash("비밀번호가 너무 짧습니다.")
        else:
            # # 비밀번호 암호화
            hashed_password = bcrypt.generate_password_hash(password1)

            user = User(username, email, hashed_password)
            db.session.add(user)
            db.session.commit()

            # 회원가입이 성공적으로 완료됨을 알리는 메시지 표시
            flash("회원가입 완료")
            return render_template('login.html')

    # GET 요청인 경우 회원가입 양식을 표시
    return render_template('register.html')

# 로그인 기능
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password1']

        user = User.query.filter_by(email=email).first()

        if user:
            if bcrypt.check_password_hash(user.password, password):
                print('로그인 완료')
                login_user(user, remember=True)
                return redirect(url_for('index'))
            else: 
                flash('비밀번호가 다릅니다.')
                return render_template('login.html')
        else:
            flash('해당 이메일 정보가 없습니다.')
            return render_template('login.html')
    else: # GET 로그인 페이지
        return render_template('login.html')

# 로그아웃 페이지
@app.route('/logout')
@login_required
def logout():
    logout_user()
    print('logout success!')
    return redirect(url_for('login'))

# 내방객 등록 페이지
@app.route('/visit', methods=['GET', 'POST'])
@login_required
def visitor():
    if request.method == 'POST':
        name = request.form['inputName']
        department = request.form['inputDepartment']
        phone = request.form['inputPhoneNumber']
        manager = request.form['inputManager']
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device = request.form['inputDevice']
        serial_number = request.form['inputSerialNumber']

        page = request.args.get('page', type=int, default=1) # 페이지
        # visitor_info = Visitor.query.all()
        visitor_info = Visitor.query.order_by('id')
        page_list = visitor_info.paginate(page=page, per_page=4)

        department_list = [
            'CJ Olivenetworks',
            'CJ 대한통운',
            'CJ 올리브영',
            'CJ CGV',
            'CJ 프레시웨이',
            '디아이웨어',
            '기타',
        ]

        visitor = Visitor(name, department, phone, manager, device, serial_number, created_time, 0)
        db.session.add(visitor)
        db.session.commit()
        return render_template('visitor.html', department_list=department_list, page_list=page_list)
    else:
        page = request.args.get('page', type=int, default=1) # 페이지
        # visitor_info = Visitor.query.all()
        visitor_info = Visitor.query.order_by('id')
        page_list = visitor_info.paginate(page=page, per_page=4)
        department_list = [
            'CJ Olivenetworks',
            'CJ 대한통운',
            'CJ 올리브영',
            'CJ CGV',
            'CJ 프레시웨이',
            '디아이웨어',
            '기타',
        ]
        return render_template('visitor.html', department_list=department_list, page_list=page_list) #visitor_info=visitor_info

# @app.route('/cjworld', methods=['GET', 'POST'])
# def login_cj():
#     if request.method == 'POST':
#         url = "http://cj.cj.net/PT/login.aspx?sLang=KOR"
#         datas = { #ID name: txtID, PW name: txtPWD
#             "txtID": 'jeonhyuk',
#             "txtPWD": 'jj119672@@'
#         }
#         response = requests.post(url, data=datas)
#         content = response.text
#         print(content)
#         email = request.form['cj_email']
#         password = request.form['cj_password1']
#         print(response)
#         return render_template('cj_login.html')

#     else: # GET 로그인 페이지
#         return render_template('cj_login.html')
    
@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    # csrf.init_app(app) # CSRF Config
    app.run(debug=True)
