#!/usr/bin/env python
from flask import Flask, flash, session, url_for, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # Password Hash
from flask_bcrypt import Bcrypt
from app import User, Visitor, Card, User_log, Visitor_log, Year, Month, Day
import jinja2.exceptions
from config import create_app, db
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager
from datetime import datetime, date, time
import asyncio

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
        device = request.form.get('inputDevice')
        remarks = request.form.get('inputRemarks')
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

        # 내방객 수정 - 부서 목록
        department_list = ['CJ Olivenetworks','CJ 대한통운','CJ 올리브영','CJ CGV','CJ 프레시웨이','디아이웨어','기타',]
        return render_template('visitor_update.html', current_user=current_user, approve_visitors=approve_visitors, visitor_count=visitor_count, time=time, card_list=card_list, department_list=department_list)

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
    visitor_log = Visitor_log.query.filter_by(visitor_id=1).first()
    print(visitor_log)
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
        visitor = Visitor(name, department, phone, manager, device, remarks, object, created_time, 0)
        db.session.add(visitor)
        db.session.commit()
        return redirect(url_for('visitor'))
    else:
        # GET - 승인되지 않은 방문객 정보
        visitor_info = Visitor.query.filter_by(approve=0)

        # 내방객 등록 - 부서 목록
        department_list = ['CJ Olivenetworks','CJ 대한통운','CJ 올리브영','CJ CGV','CJ 프레시웨이','디아이웨어','기타',]

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
        year.count += 1
        month.count += 1
    else:
        year.count += 1
        month.count += 1
        day.count += 1

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
        year.count += 1
        month.count += 1
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
        update_visitor_info = [update_visitor.id, update_visitor.name, update_visitor.department, update_visitor.object, update_visitor.phone, update_visitor.manager, update_visitor.device, update_visitor.remarks]
        return jsonify(response=update_visitor_info)

# manage visit 삭제 api
@app.route('/api/ajax_delete_manage_visit', methods=['POST'])
def ajax_delete_manage_visit():
    data = request.get_json()
    visitor = data['delete_btn']
    delete_visitor = Visitor.query.filter_by(id=visitor).first()
    db.session.delete(delete_visitor)
    db.session.commit()
    return jsonify()

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    # csrf.init_app(app) # CSRF Config
    app.run(debug=True)
