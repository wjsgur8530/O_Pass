#!/usr/bin/env python
from flask import Flask, flash, session, url_for, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # Password Hash
from flask_bcrypt import Bcrypt
from app import User, Visitor, Card
import jinja2.exceptions
from config import create_app, db
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager
from datetime import datetime, date, time
import qrcode
import requests

app = create_app()
bcrypt = Bcrypt(app)

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = u"로그인 후에 서비스를 이용해주세요."
login_manager.login_message_category = "info"
@login_manager.user_loader
def load_user(id):
    return db.session.get(User, id)  # primary_key

@app.route('/')
@app.route('/index')
@login_required
def index():
    # 타임 스탬프
    today_weekday = datetime.now().weekday()
    weekdays = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}
    weekday = weekdays.get(today_weekday, "")
    current_date = datetime.now().strftime('%Y년 %m월 %d일 ') + weekday
    current_time = datetime.now().strftime('\n%p %H:%M:%S')
    time = [ current_date, current_time]

    # 실시간 출입 방문객
    in_visitor = Visitor.query.filter_by(exit=0)
    in_visitor = in_visitor.count()

    # 승인된 방문객 Sort_Desc
    approve_visitors = Visitor.query.filter_by(approve=1).order_by(Visitor.id.desc())
    print(approve_visitors.count())

    card_list = Card.query.all()

    visitor_count = []
    daily_visitor = approve_visitors.count()
    visitor_count = [
        daily_visitor, #일간 방문자
        in_visitor,
    ]
    
    # print('현재 로그인한 사용자: ' + str(current_user))
    return render_template('index.html', current_user=current_user, approve_visitors=approve_visitors, visitor_count=visitor_count, time=time, card_list=card_list)

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
        department = request.form['registerDepartment']

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

            user = User(username, email, hashed_password, department)
            db.session.add(user)
            db.session.commit()

            # 회원가입이 성공적으로 완료됨을 알리는 메시지 표시
            flash("회원가입 완료")
            return redirect('login')

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
                return redirect(url_for('index', user=user.username))
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
        object = request.form['inputObject']
        phone = request.form['inputPhoneNumber']
        manager = request.form['inputManager']
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device = request.form['inputDevice']
        serial_number = request.form['inputSerialNumber']

        # visitor_info = Visitor.query.all()
        visitor_info = Visitor.query.filter_by(approve=0)

        department_list = [
            'CJ Olivenetworks',
            'CJ 대한통운',
            'CJ 올리브영',
            'CJ CGV',
            'CJ 프레시웨이',
            '디아이웨어',
            '기타',
        ]
        # 내방객 등록하기
        visitor = Visitor(name, department, phone, manager, device, serial_number, object, created_time, 0)
        db.session.add(visitor)
        db.session.commit()
        return render_template('visitor.html', department_list=department_list, visitor_info=visitor_info)
    else:
        # visitor_info = Visitor.query.all()
        visitor_info = Visitor.query.filter_by(approve=0)
        department_list = [
            'CJ Olivenetworks',
            'CJ 대한통운',
            'CJ 올리브영',
            'CJ CGV',
            'CJ 프레시웨이',
            '디아이웨어',
            '기타',
        ]
        return render_template('visitor.html', department_list=department_list, visitor_info=visitor_info)

# 테이블 테스트
@app.route('/tables_test', methods=['GET', 'POST'])
@login_required
def table_test():
    approve_visitors = Visitor.query.filter_by(approve=1)
    return render_template('tables_test.html', approve_visitors=approve_visitors)

# 승인 버튼 클릭시 로직 ajax
@app.route('/api/ajax_approve', methods=['POST'])
def ajax_approve():
    data = request.get_json()
    print(data['visitor_id'])
    print(data['approve'])
    visitor = Visitor.query.filter_by(id=data['visitor_id']).first()
    visitor.approve = 1
    visitor.exit = 0
    db.session.commit()
    return jsonify(result = "success")

# 반려 버튼 클릭시 로직 ajax
@app.route('/api/ajax_deny', methods=['POST'])
def ajax_deny():
    data = request.get_json()
    print(data['visitor_id'])
    print(data['approve'])
    visitor = Visitor.query.filter_by(id=data['visitor_id']).first()
    db.session.delete(visitor)
    db.session.commit()
    return jsonify(result = "success")

# 퇴실 버튼 클릭시 로직 ajax
@app.route('/api/ajax_exit', methods=['POST'])
def ajax_exit():
    data = request.get_json()
    visitor = Visitor.query.filter_by(id=data['exit_id']).first()

    if visitor.card_id is None: # 카드를 안 받은 사람은 퇴실 X
        return "오류 발생"

    if visitor.exit_date == None and visitor.exit == 0:
        visitor.exit_date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        visitor.exit = 1
        card = Card.query.filter_by(id=visitor.card_id).first()
        card.card_status = "회수"
        db.session.commit()
    return jsonify(result = "success")

# index 체크 박스 퇴실 api
@app.route('/api/ajax_index_exit_checkbox', methods=['POST'])
def ajax_index_exit_checkbox():
    data = request.get_json()
    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        if visitor.exit_date == None and visitor.exit == 0:
            visitor.exit_date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            visitor.exit = 1
            card = Card.query.filter_by(id=visitor.card_id).first()
            card.card_status = "회수"
            db.session.commit()
    return jsonify(result = "success")

# visit 체크 박스 승인 api
@app.route('/api/ajax_visit_approve_checkbox', methods=['POST'])
def ajax_visit_approve_checkbox():
    data = request.get_json()
    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        visitor.approve = 1
        visitor.exit = 0
        db.session.commit()
    return jsonify(result = "success")

# visit 체크 박스 반려 api
@app.route('/api/ajax_visit_deny_checkbox', methods=['POST'])
def ajax_visit_deny_checkbox():
    data = request.get_json()
    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        db.session.delete(visitor)
        db.session.commit()
    return jsonify(result = "success")

# index 담당자 업데이트 체크 박스 api
@app.route('/api/ajax_index_manager_update_checkbox', methods=['POST'])
def ajax_index_manager_update_checkbox():
    data = request.get_json()
    manager = data['manager']
    print(data['manager'])
    if manager:
        for checked_data in data['checked_datas']:
            visitor = Visitor.query.filter_by(id=checked_data).first()
            visitor.manager = manager
            db.session.commit()
        return jsonify(result = "success")
    return jsonify(result = "error")

# index 카드 불출 체크 박스 api
@app.route('/api/ajax_index_card_checkbox', methods=['POST'])
def ajax_index_card_checkbox():
    data = request.get_json()
    card = data['card']
    data_length = len(data['checked_datas']) # 선택된 체크박스 수

    if card is None or data_length != 1: # 선택한 카드가 없거나 2개 이상 선택됐을 때 오류 발생
        return "오류 발생"

    card_table = Card.query.filter_by(card_type=card).first()
    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        if visitor.exit != 1 and visitor.card_id == None:
            visitor.card_id = card_table.id
            card_table.card_status = "불출"
            db.session.commit()
        else:
            return "오류 발생"
    return jsonify(result = "success")

# DB 카드 생성 로직
@app.route('/api/create_card', methods=['POST'])
def create_card():
    # 출입 카드 DB Content 생성
    categories = ['일반', '공사', '전산']
    elements = [f'{category}{i}' for category in categories for i in range(1, 16)]
    for i in elements:
        card = Card(i, '회수')
        db.session.add(card)
        db.session.commit()
    return "Cretaed Card"

# @app.route('/abc')
# def count_visitors():
#     today = datetime.today().date()
#     print(today)
    # # 일간 방문자 수 카운트 및 저장
    # daily_visitors = Visitors.query.filter_by(date=today).first()
    # if daily_visitors:
    #     daily_visitors.visitors += 1
    # else:
    #     daily_visitors = Visitors(date=today, visitors=1)
    #     db.session.add(daily_visitors)
    
    # # 주간 방문자 수 카운트 및 저장
    # start_of_week = today - timedelta(days=today.weekday())
    # end_of_week = start_of_week + timedelta(days=6)
    # weekly_visitors = Visitors.query.filter(Visitors.date.between(start_of_week, end_of_week)).first()
    # if weekly_visitors:
    #     weekly_visitors.visitors += 1
    # else:
    #     weekly_visitors = Visitors(date=start_of_week, visitors=1)
    #     db.session.add(weekly_visitors)
    
    # # 월간 방문자 수 카운트 및 저장
    # start_of_month = today.replace(day=1)
    # end_of_month = start_of_month + timedelta(days=31)  # 최대 31일로 설정 (조정 필요)
    # monthly_visitors = Visitors.query.filter(Visitors.date.between(start_of_month, end_of_month)).first()
    # if monthly_visitors:
    #     monthly_visitors.visitors += 1
    # else:
    #     monthly_visitors = Visitors(date=start_of_month, visitors=1)
    #     db.session.add(monthly_visitors)
    
    # # 연간 방문자 수 카운트 및 저장
    # start_of_year = today.replace(month=1, day=1)
    # end_of_year = start_of_year.replace(month=12, day=31)
    # yearly_visitors = Visitors.query.filter(Visitors.date.between(start_of_year, end_of_year)).first()
    # if yearly_visitors:
    #     yearly_visitors.visitors += 1
    # else:
    #     yearly_visitors = Visitors(date=start_of_year, visitors=1)
    #     db.session.add(yearly_visitors)
    
    # db.session.commit()
    
    # return '방문자 수 카운트 완료'


@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    # csrf.init_app(app) # CSRF Config
    app.run(debug=True)
