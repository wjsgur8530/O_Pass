#!/usr/bin/env python
from flask import Flask, flash, session, url_for, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # Password Hash
from flask_bcrypt import Bcrypt
from app import User, Visitor, Card, User_log, Year, Month, Day, Department
import jinja2.exceptions
from config import create_app, db
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager
from datetime import datetime, date, time
import qrcode
import mysql.connector
import openpyxl
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
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

    # 승인된 방문객 Sort_Desc
    approve_visitors = Visitor.query.filter_by(approve=1).order_by(Visitor.id.desc())

    # 출입 카드 목록
    card_list = Card.query.all()

    if approve_visitors:
        # 실시간 출입 방문객
        in_visitor = Visitor.query.filter_by(exit=0)
        in_visitor_card_none = Visitor.query.filter_by(exit=0, card_id=None)

        # 실시간 출입 방문객 카운팅
        in_visitor = in_visitor.count()
        in_visitor_card_none = in_visitor_card_none.count()
        in_visitor = in_visitor - in_visitor_card_none

        today = date.today()
        year = Year.query.filter_by(year=today.year).first() # 연간 방문객
        month = Month.query.filter_by(year=today.year, month=today.month).first() # 월간 방문객
        day = Day.query.filter_by(year=today.year, month=today.month, day=today.day).first() # 일간 방문객
        if year:
            yearly_visitor = year.count
            if month:
                monthly_visitor = month.count
                if day:
                    daily_visitor = day.count
                    visitor_count = [in_visitor, yearly_visitor, monthly_visitor, daily_visitor]
                else:
                    visitor_count = [in_visitor, yearly_visitor, monthly_visitor, 0]
            else:
                visitor_count = [in_visitor, yearly_visitor, 0, 0]
        else:
            visitor_count = [in_visitor, 0, 0, 0]
    
    # print('현재 로그인한 사용자: ' + str(current_user))
    return render_template('index.html', current_user=current_user, approve_visitors=approve_visitors, visitor_count=visitor_count, time=time, card_list=card_list)

# 방문객 관리 페이지
@app.route('/manage_visitors', methods=['GET', 'POST'])
def manage_visitors():
    if request.method == 'POST':
        update_id = request.form['inputUpdateNumber']
        name = request.form['inputName']
        department = request.form['inputDepartment']
        phone = request.form['inputPhoneNumber']
        manager = request.form['inputManager']
        location = request.form['inputLocation']
        device = request.form.get('inputDevice')
        remarks = request.form.get('inputRemarks')
        object = request.form.get('inputObject')
        # print(update_id)

        update_visitor = Visitor.query.filter_by(id=update_id).first()
        update_visitor.name = name
        update_visitor.department = department
        update_visitor.phone = phone
        update_visitor.manager = manager
        if device == '1':
            update_visitor.device = True
        else:
            update_visitor.device = False
        update_visitor.remarks = remarks
        update_visitor.location = location
        update_visitor.object = object
        db.session.commit()
        return redirect('manage_visitors')
    else:
        # 타임 스탬프
        today_weekday = datetime.now().weekday()
        weekdays = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}
        weekday = weekdays.get(today_weekday, "")
        current_date = datetime.now().strftime('%Y년 %m월 %d일 ') + weekday
        current_time = datetime.now().strftime('\n%p %H:%M:%S')
        time = [ current_date, current_time]

        # 승인된 방문객 Sort_Desc
        approve_visitors = Visitor.query.filter_by(approve=1).order_by(Visitor.id.desc())

        # 출입 카드 목록
        card_list = Card.query.all()

        if approve_visitors:
            # 실시간 출입 방문객
            in_visitor = Visitor.query.filter_by(exit=0)
            in_visitor_card_none = Visitor.query.filter_by(exit=0, card_id=None)

            # 실시간 출입 방문객 카운팅
            in_visitor = in_visitor.count()
            in_visitor_card_none = in_visitor_card_none.count()
            in_visitor = in_visitor - in_visitor_card_none

            today = date.today()
            year = Year.query.filter_by(year=today.year).first() # 연간 방문객
            month = Month.query.filter_by(year=today.year, month=today.month).first() # 월간 방문객
            day = Day.query.filter_by(year=today.year, month=today.month, day=today.day).first() # 일간 방문객
            if year:
                yearly_visitor = year.count
                if month:
                    monthly_visitor = month.count
                    if day:
                        daily_visitor = day.count
                        visitor_count = [in_visitor, yearly_visitor, monthly_visitor, daily_visitor]
                    else:
                        visitor_count = [in_visitor, yearly_visitor, monthly_visitor, 0]
                else:
                    visitor_count = [in_visitor, yearly_visitor, 0, 0]
            else:
                visitor_count = [in_visitor, 0, 0, 0]

        # 내방객 등록 - 부서 목록
        department_lists = Department.query.order_by(Department.id.asc())
        print(department_lists)
        return render_template('visitor_update.html', current_user=current_user, approve_visitors=approve_visitors, visitor_count=visitor_count, time=time, card_list=card_list, department_lists=department_lists)

# department 부서 관리 페이지
@app.route('/departments', methods=['GET', 'POST'])
def manage_departments():
    if request.method == 'POST':
        department_type = request.form['select_department_type']
        department_name = request.form['add_department_name_value']
        department = Department(department_type, department_name)
        db.session.add(department)
        db.session.commit()
        return redirect('departments')
    else:
        departments = Department.query.all()
        department_subsidiary = Department.query.filter_by(department_type="계열사").count()
        department_partner = Department.query.filter_by(department_type="협력사").count()
        department_bp = Department.query.filter_by(department_type="BP").count()
        department_etc = Department.query.filter_by(department_type="기타").count()
        department_counts = [department_subsidiary, department_partner, department_bp, department_etc]
        return render_template('manage_department.html', departments=departments, department_counts=department_counts)

# visit 수정 api
@app.route('/visit_update', methods=['GET', 'POST'])
def visit_update():
    if request.method == 'POST':
        update_id = request.form['inputUpdateNumber']
        name = request.form['inputUpdateName']
        department = request.form['inputUpdateDepartment']
        phone = request.form['inputUpdatePhoneNumber']
        manager = request.form['inputUpdateManager']
        location = request.form['inputUpdateLocation']
        device = request.form.get('inputUpdateDevice')
        remarks = request.form.get('inputUpdateRemarks')
        object = request.form.get('inputUpdateObject')

        update_visitor = Visitor.query.filter_by(id=update_id).first()
        update_visitor.name = name
        update_visitor.department = department
        update_visitor.phone = phone
        update_visitor.manager = manager
        if device == '1':
            update_visitor.device = True
        else:
            update_visitor.device = False
        update_visitor.remarks = remarks
        update_visitor.location = location
        update_visitor.object = object
        db.session.commit()
        return redirect('visit')

# 카드 관리 페이지
@app.route('/manage_cards', methods=['GET', 'POST'])
def manage_cards():
    card_num = 0
    in_card_num = 0
    card_1 = []
    card_2 = []
    card_3 = []
    in_card_1 = []
    in_card_2 = []
    in_card_3 = []
    
    cards = Card.query.all()
    for card in cards:
        if '일반' in card.card_type:
            card_1.append(card.card_type)
            card_num += 1
        elif '공사' in card.card_type:
            card_2.append(card.card_type)
            card_num += 1
        else:
            card_3.append(card.card_type)
            card_num += 1

    in_cards = Card.query.filter_by(card_status='회수').all()
    for in_card in in_cards:
        if '일반' in in_card.card_type:
            in_card_1.append(in_card.card_type)
            in_card_num += 1
        elif '공사' in in_card.card_type:
            in_card_2.append(in_card.card_type)
            in_card_num += 1
        else:
            in_card_3.append(in_card.card_type)
            in_card_num += 1
    
    visitor = Visitor.query.all()
    total_card = [card_1, card_2, card_3, in_card_1, in_card_2, in_card_3, card_num, in_card_num,
                  len(card_1), len(card_2), len(card_3), len(in_card_1), len(in_card_2), len(in_card_3), in_cards, visitor]

    return render_template('manage_cards.html', total_card=total_card)

# 로그 관리 페이지
@app.route('/manage_logs', methods=['GET', 'POST'])
def manage_logs():
    user_log = User_log.query.all()
    visitors = Visitor.query.all()
    return render_template('manage_logs.html', user_log=user_log)

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
        rank = request.form['registerRank']

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

            user = User(username, email, hashed_password, department, rank)
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
        current_date = datetime.now()
        email = request.form['email']
        password = request.form['password1']

        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                print('로그인 완료')
                login_user(user, remember=True)
                user_log = User_log(request.remote_addr, current_date, user.id)
                db.session.add(user_log)
                db.session.commit()
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
    # 현재 시간
    current_date = datetime.now()
    # 현재 로그인된 사용자 중 가장 마지막 접속 기록 ID 추출
    logout_log = User_log.query.filter_by(user_id=current_user.id).order_by(User_log.id.desc()).first()
    # 마지막 접속 ID의 로그아웃 스탬프 컬럼에 현재 시간 기록
    logout_log.logout_timestamp = current_date
    # DB 적용
    db.session.commit()
    # 로그아웃 수행
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
        location = request.form['inputLocation']
        manager = request.form['inputManager']
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device = request.form.get('inputDevice')
        remarks = request.form.get('inputRemarks')
        if device:
            device = True
            remarks = request.form.get('inputRemarks')
        else:
            device = False
            remarks = None

        # 내방객 등록하기
        visitor = Visitor(name, department, phone, location, manager, device, remarks, object, created_time, 0, "사전 등록")
        db.session.add(visitor)
        db.session.commit()
        return redirect(url_for('visitor'))
    else:
        # GET - 승인되지 않은 방문객 정보
        visitor_info = Visitor.query.filter_by(approve=0)

        # 내방객 등록 - 부서 목록
        department_lists = Department.query.order_by(Department.id.asc())
        print(department_lists)
        return render_template('visitor.html', department_lists=department_lists, visitor_info=visitor_info)

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
    visitor.approve_log = current_user.id

    today = date.today()
    year = Year.query.filter_by(year=today.year).first()
    if not year:
        year = Year(year=today.year, count=1)
        db.session.add(year)

    month = Month.query.filter_by(year=today.year, month=today.month).first()
    if not month:
        month = Month(year=today.year, month=today.month, count=1)
        db.session.add(month)

    day = Day.query.filter_by(year=today.year, month=today.month, day=today.day).first()
    if not day:
        day = Day(year=today.year, month=today.month, day=today.day, count=1)
        db.session.add(day)

    else:
        year.count += 1
        month.count += 1
        day.count += 1

    if visitor.device == 0:
        device = "미반입"
    else:
        device = "반입"

    if visitor.registry == "사전 등록":
        #register_send_sms(visitor.name, visitor.created_date, visitor.object, visitor.location, visitor.manager, visitor.phone, device)
        image_send_sms_previous(visitor.name, visitor.created_date, visitor.object, visitor.location, visitor.manager, visitor.phone, device)
    else:
        image_send_sms_current(visitor.name, visitor.created_date, visitor.object, visitor.location, visitor.manager, visitor.phone, device)

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

# 긴급 승인 버튼 클릭시 로직 ajax
@app.route('/api/ajax_emergency_approve', methods=['POST'])
def ajax_emergency_approve():
    data = request.get_json()
    print(data['visitor_id'])
    print(data['approve'])

    visitor = Visitor.query.filter_by(id=data['visitor_id']).first()
    visitor.approve = 1
    visitor.exit = 0

    today = date.today()
    year = Year.query.filter_by(year=today.year).first()
    if not year:
        year = Year(year=today.year, count=1)
        db.session.add(year)

    month = Month.query.filter_by(year=today.year, month=today.month).first()
    if not month:
        month = Month(year=today.year, month=today.month, count=1)
        db.session.add(month)

    day = Day.query.filter_by(year=today.year, month=today.month, day=today.day).first()
    if not day:
        day = Day(year=today.year, month=today.month, day=today.day, count=1)
        db.session.add(day)
    else:
        year.count += 1
        month.count += 1
        day.count += 1

    db.session.commit()
    return jsonify(result = "success")

# index 퇴실 버튼 클릭시 로직 ajax
@app.route('/api/ajax_exit', methods=['POST'])
def ajax_exit():
    data = request.get_json()
    visitor = Visitor.query.filter_by(id=data['exit_id']).first()

    if visitor.card_id is None: # 카드를 안 받은 사람은 퇴실 X
        return "Card None"

    if visitor.exit_date == None and visitor.exit == 0:
        visitor.exit_date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        visitor.exit = 1
        visitor.card.card_status = "회수"
        visitor.card_id = None
        visitor.exit_log = current_user.id
        db.session.commit()
    else:
        return "Exit Error"

    return jsonify(response = "success")

# index 체크 박스 퇴실 api
@app.route('/api/ajax_index_exit_checkbox', methods=['POST'])
def ajax_index_exit_checkbox():
    data = request.get_json()
    data_length = len(data['checked_datas'])

    if data_length < 1:
        return "No Select"

    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        if visitor.exit == 1:
            return "Exited"
        if visitor.card_id is None:
            return "No Card"

        if visitor.exit_date == None and visitor.exit == 0:
            visitor.exit_date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            visitor.exit = 1
            visitor.card.card_status = "회수"
            visitor.card_id = None
            visitor.exit_log = current_user.id
            db.session.commit()
        else:
            return "Exited"
    return jsonify(result = "success")

# visit 체크 박스 승인 api
@app.route('/api/ajax_visit_approve_checkbox', methods=['POST'])
def ajax_visit_approve_checkbox():
    data = request.get_json()
    data_length = len(data['checked_datas'])

    if data_length < 1:
        return "No Select"

    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        visitor.approve = 1
        visitor.exit = 0
        visitor.approve_log = current_user.id

        today = date.today()
        year = Year.query.filter_by(year=today.year).first()
        if not year:
            year = Year(year=today.year, count=1)
            db.session.add(year)

        month = Month.query.filter_by(year=today.year, month=today.month).first()
        if not month:
            month = Month(year=today.year, month=today.month, count=1)
            db.session.add(month)

        day = Day.query.filter_by(year=today.year, month=today.month, day=today.day).first()
        if not day:
            day = Day(year=today.year, month=today.month, day=today.day, count=1)
            db.session.add(day)
        else:
            year.count += 1
            month.count += 1
            day.count += 1

        if visitor.device == 0:
            device = "미반입"
        else:
            device = "반입"

        register_send_sms(visitor.name, visitor.created_date, visitor.object, visitor.location, visitor.manager, visitor.phone, device)
        db.session.commit()
    return jsonify(result = "success")

# visit 체크 박스 반려 api
@app.route('/api/ajax_visit_deny_checkbox', methods=['POST'])
def ajax_visit_deny_checkbox():
    data = request.get_json()
    data_length = len(data['checked_datas'])

    if data_length < 1:
        return "No Select"

    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        db.session.delete(visitor)
        db.session.commit()
    return jsonify(result = "success")

# visit 체크 박스 긴급 승인 api - G6에게 이메일, 문자메세지
@app.route('/api/ajax_visit_emergency_approve_checkbox', methods=['POST'])
def ajax_visit_emergency_approve_checkbox():
    data = request.get_json()
    data_length = len(data['checked_datas'])

    if data_length < 1:
        return "No Select"

    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        visitor.approve = 1
        visitor.exit = 0

        today = date.today()
        year = Year.query.filter_by(year=today.year).first()
        if not year:
            year = Year(year=today.year)
            db.session.add(year)

        month = Month.query.filter_by(year=today.year, month=today.month).first()
        if not month:
            month = Month(year=today.year, month=today.month)
            db.session.add(month)
            year.count += 1

        day = Day.query.filter_by(year=today.year, month=today.month, day=today.day).first()
        if not day:
            day = Day(year=today.year, month=today.month, day=today.day, count=1)
            db.session.add(day)
            month.count += 1
        else:
            year.count += 1
            month.count += 1
            day.count += 1

        db.session.commit()
    return jsonify(result = "success")

# index 담당자 업데이트 체크 박스 api
@app.route('/api/ajax_index_manager_update_checkbox', methods=['POST'])
def ajax_index_manager_update_checkbox():
    data = request.get_json()
    manager = data['manager']
    data_length = len(data['checked_datas'])

    if data_length < 1:
        return "No Select"
    if manager is None or manager == "":
        return "Error"

    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        if visitor.exit == 1:
            return "Exited"
        visitor.manager = manager
        db.session.commit()
    return jsonify(result = "success")

# index 카드 불출 체크 박스 api
@app.route('/api/ajax_index_card_checkbox', methods=['POST'])
def ajax_index_card_checkbox():
    data = request.get_json()
    card = data['card']
    data_length = len(data['checked_datas']) # 선택된 체크박스 수

    # 선택한 카드가 없거나 2개 이상 선택됐을 때 오류 발생
    if card is None:
        return "No Card"
    if data_length < 1:
        return "No Select"
    if data_length != 1:
        return "Multi Check"

    card_table = Card.query.filter_by(card_type=card).first()
    for checked_data in data['checked_datas']:
        visitor = Visitor.query.filter_by(id=checked_data).first()
        if visitor.exit == 1:
            return "Exited"
        if visitor.card_id != None:
            return "Use Card"

        visitor.card_id = card_table.id
        card_table.card_status = "불출"
        db.session.commit()
    return jsonify(result = "success")

# update visit 카드 회수 체크 박스 api
@app.route('/api/ajax_update_visit_recall_card_checkbox', methods=['POST'])
def ajax_update_visit_recall_card_checkbox():
    data = request.get_json()
    checked_datas = data['checked_datas']
    data_length = len(data['checked_datas']) # 선택된 체크박스 수
    print(checked_datas)

    # 선택한 카드가 없음
    if data_length < 1:
        return "No Select"
    
    for checked_data in checked_datas:
        recall_visitor = Visitor.query.filter_by(id=checked_data).first()
        if recall_visitor.card_id == None:
            return "No Card"
        if recall_visitor.exit == 1:
            return "Exited"
        recall_visitor.card.card_status = "회수"
        recall_visitor.card_id = None
        db.session.commit()
    return jsonify(result = "success")

# cards 카드 추가 api
@app.route('/api/ajax_add_card', methods=['POST'])
def ajax_add_card():
    data = request.get_json()
    card_number = data['add_card_value']
    card_type = data['select_card_type']
    print(card_number, card_type)
    if card_number == 0:
        return "No Number"
    return jsonify(result = "success")

# DB 카드 생성 로직
@app.route('/api/create_card', methods=['GET'])
def create_card():
    # 출입 카드 DB Content 생성
    categories = ['일반', '공사', '전산']
    elements = [f'{category}{i}' for category in categories for i in range(1, 16)]
    for i in elements:
        card = Card(i, '회수')
        db.session.add(card)
        db.session.commit()
    return "Cretaed Card"

# manage visit 수정 api
@app.route('/api/ajax_update_manage_visit', methods=['POST'])
def ajax_update_manage_visit():
    data = request.get_json()
    visitor = data['update_btn']
    update_visitor = Visitor.query.filter_by(id=visitor).first()
    if update_visitor.card_id != None:
        return "Use Card"
    else:
        update_visitor_info = [update_visitor.id, update_visitor.name, update_visitor.department, update_visitor.object, update_visitor.phone, update_visitor.manager, update_visitor.device, update_visitor.remarks, update_visitor.location]
        return jsonify(response=update_visitor_info)

# manage visit 삭제 api
@app.route('/api/ajax_delete_manage_visit', methods=['POST'])
def ajax_delete_manage_visit():
    data = request.get_json()
    visitor = data['delete_btn']
    delete_visitor = Visitor.query.filter_by(id=visitor).first()
    if delete_visitor.card_id != None:
        return "Use Card"
    db.session.delete(delete_visitor)
    db.session.commit()
    return jsonify()

# manage qr 재전송 api
@app.route('/api/ajax_manage_qrcode_send', methods=['POST'])
def ajax_manage_qrcode_send():
    data = request.get_json()
    qrcode_id = data['qrcode_btn']
    print(qrcode_id)
    qrcode_visitor = Visitor.query.filter_by(id=qrcode_id).first()
    print(qrcode_visitor.phone)
    if qrcode_visitor.card_id:
        return "Use Card"
    send_sms(qrcode_visitor.name, qrcode_visitor.created_date, qrcode_visitor.object, qrcode_visitor.location, qrcode_visitor.manager, qrcode_visitor.phone)
    return jsonify()

# 부서 삭제 api
@app.route('/api/ajax_department_delete', methods=['POST'])
def ajax_department_delete():
    data = request.get_json()
    print(data['delete_id'])
    delete_id = data['delete_id']
    department = Department.query.filter_by(id=delete_id).first()
    db.session.delete(department)
    db.session.commit()
    return jsonify()

# SMS-TEXT 문자 메세지 보내기 - 현장 등록 완료
def send_sms(name, date, object, location, manager, phone_num):
    cursor = app.mysql_conn.cursor()  # 커서 생성
    # insert_query = "INSERT INTO sms_msg (REQDATE, STATUS, TYPE, PHONE, CALLBACK, MSG) VALUES (%s, %s, %s, %s, %s, %s)"
    insert_query = "INSERT INTO mms_msg (REQDATE, STATUS, TYPE, PHONE, CALLBACK, SUBJECT, MSG, FILE_CNT) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    msg = '안녕하세요. ' + name + '님\n' + '송도 IDC 센터에 방문하신 것을 환영합니다.\n-방문시간: ' + str(date) + '\n-방문목적: ' + object + '\n-작업위치: ' + location + '\n-담당자: ' + manager

    insert_data = (datetime.now(), '1', '0', phone_num, '01057320071', '[내방객 출입 관리 시스템 현장 등록 완료]', msg, '1')  # 삽입할 데이터를 튜플로 정의
    cursor.execute(insert_query, insert_data)  # 쿼리 실행 및 데이터 전달
    app.mysql_conn.commit()  # 변경 사항 커밋
    cursor.close()  # 커서 닫기

# MMS-IMAGE TEST SMS 문자 메세지 보내기 - 현장 등록 승인
def image_send_sms_current(name, date, object, location, manager, phone_num, device):
    cursor = app.mysql_conn.cursor()  # 커서 생성
    insert_query = "INSERT INTO mms_msg (REQDATE, STATUS, TYPE, PHONE, CALLBACK, SUBJECT, MSG, FILE_CNT) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    msg =  name + '님 ' + '안녕하세요.\n' + '송도 IDC 센터에 방문하신 것을 환영합니다.\n-등록시간: ' + str(date) + '\n-방문위치: 인천광역시 연수구 하모니로177번길 20' + '\n-방문목적: ' + object + '\n-장비반입: ' + device + '\n-작업위치: ' + location + '\n-담당자: ' + manager + '\n-QR Code◀ '

    insert_data = (datetime.now(), '1', '0', phone_num, '01057320071', '[내방객 출입 관리 시스템 현장 등록 승인]', msg, '2', 'I', 'D://CJAgent//qr_img.jpg')  # 삽입할 데이터를 튜플로 정의
    cursor.execute(insert_query, insert_data)  # 쿼리 실행 및 데이터 전달
    app.mysql_conn.commit()  # 변경 사항 커밋
    cursor.close()  # 커서 닫기

# MMS-IMAGE TEST SMS 문자 메세지 보내기 - 사전 등록 승인
def image_send_sms_previous(name, date, object, location, manager, phone_num, device):
    cursor = app.mysql_conn.cursor()  # 커서 생성
    insert_query = "INSERT INTO mms_msg (REQDATE, STATUS, TYPE, PHONE, CALLBACK, SUBJECT, MSG, FILE_CNT, FILE_TYPE1, FILE_PATH1) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    msg = name + '님 ' + '안녕하세요.\n' + '송도 IDC 센터에 방문하신 것을 환영합니다.\n-등록시간: ' + str(date) + '\n-방문위치: 인천광역시 연수구 하모니로177번길 20' + '\n-방문목적: ' + object + '\n-장비반입: ' + device + '\n-작업위치: ' + location + '\n-담당자: ' + manager + '\n-QR Code◀ '

    insert_data = (datetime.now(), '1', '0', phone_num, '01057320071', '[내방객 출입 관리 시스템 사전 등록 승인]', msg, '2', 'I', 'D://CJAgent//qr_img.jpg')  # 삽입할 데이터를 튜플로 정의
    cursor.execute(insert_query, insert_data)  # 쿼리 실행 및 데이터 전달
    app.mysql_conn.commit()  # 변경 사항 커밋
    cursor.close()  # 커서 닫기

@app.route('/api/ajax_excel_download', methods=['GET', 'POST'])
def ajax_excel_download():
    data = request.get_json()
    print(data)
    start_date = data['start_date_val']
    end_date = data['end_date_val']
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    headers = [
        '번호', '입실일시', '퇴실일시', '출입목적', '요청인소속', '출입요청인', '전화번호', 
        '작업위치', '작업내용', '장비반입', '담당자', 'SR 요청번호', '비고'
    ]

    # 헤더 쓰기
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        cell = sheet[col_letter + '5']
        cell.value = header
        cell.alignment = Alignment(horizontal='center', vertical='center')
        sheet.column_dimensions[col_letter].width = 20

    # 데이터 쓰기
    exited_visitors = Visitor.query.filter_by(exit=1)
    for row_num, exited_visitor in enumerate(exited_visitors, 6):
        row = (
            exited_visitor.id, exited_visitor.created_date, exited_visitor.exit_date,
            exited_visitor.object, exited_visitor.department, exited_visitor.name,
            exited_visitor.phone, exited_visitor.location, "",
            exited_visitor.device, exited_visitor.manager,
            "", exited_visitor.remarks
        )
        sheet.append(row)

        for col_num, _ in enumerate(row, 1):
            col_letter = get_column_letter(col_num)
            cell = sheet[col_letter + str(row_num)]
            cell.alignment = Alignment(horizontal='center', vertical='center')

    workbook.save(start_date + '-' + end_date + ' 내방객 출입점검 일지1.xlsx')
    return jsonify(result="success")

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

# MySQL 데이터베이스에 연결하는 함수
def connect_to_database():
    app.config['DB_HOST'] = 'localhost'
    app.config['DB_USER'] = 'root'
    app.config['DB_PASSWORD'] = '1q2w3e4r'
    app.config['DB_DATABASE'] = 'o_pass'
    app.config['DB_PORT'] = '3307'
    app.mysql_conn = mysql.connector.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_DATABASE'],
        port=app.config['DB_PORT']
    )

if __name__ == '__main__':
    connect_to_database()
    # csrf.init_app(app) # CSRF Config
    app.run(debug=True)
