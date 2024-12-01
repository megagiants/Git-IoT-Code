from flask import Flask, jsonify, request, session, logging, render_template
from flask_cors import CORS
from flask_session import Session
import mysql.connector
from redis import StrictRedis
from datetime import timedelta
from redis.connection import Encoder
import json

class SafeEncoder(Encoder):
    def decode(self, value):
        try:
            return super().decode(value)
        except UnicodeDecodeError:
            return value  # 디코딩 실패 시 원본 값 반환

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.secret_key = '12345678'

#app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = StrictRedis(
    host='master.redis-iot.diaewk.apn2.cache.amazonaws.com',
    port=6379,
    decode_responses=False,  # 디코딩 문제 방지
)
app.session_interface = Session(app)  # SafeEncoder를 적용

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 세션 유효 기간 설정
app.config['SESSION_SERIALIZER'] = json
Session(app)

db = mysql.connector.connect(
    host="prduserdata.c5keiyccyg3f.ap-northeast-2.rds.amazonaws.com",
    user="root",
    password="12345678",
    database="user"
)
cursor = db.cursor()

# 회원가입 화면
@app.route("/signup")
def signup_page():
    return render_template("signup.html")

# 로그인 화면
@app.route("/")
def login_page():
    return render_template("index.html")

# 대시보드 화면
@app.route("/dashboard")
def dashboard_page():
    try:
        # 세션 확인
        if 'user_id' in session:
            user_name = session.get('user_name', 'Guest')
            app.logger.info(f"대시보드 요청: user_id={session['user_id']}, user_name={user_name}")
            return render_template("dashboard.html", user_name=user_name)

        # 세션이 없는 경우
        app.logger.warning("Unauthorized access to /dashboard - 세션이 없습니다.")
        return "Unauthorized - Session expired", 401
    except Exception as e:
        app.logger.error(f"Dashboard 페이지에서 오류 발생: {e}")
        return "Internal Server Error", 500

# 마이페이지 화면
@app.route("/mypage")
def mypage_page():
    if 'user_id' in session:
        user_id = session.get('user_id')
        user_name = session.get('user_name')

        # 데이터베이스에서 연락처 가져오기
        try:
            cursor.execute("SELECT Contact FROM user WHERE ID = %s", (user_id,))
            contact_result = cursor.fetchone()
            if contact_result:
                user_contact = contact_result[0]
            else:
                user_contact = "알 수 없음"  # 연락처가 없는 경우 기본값
        except Exception as e:
            app.logger.error(f"Error fetching user contact: {e}")
            user_contact = "데이터 조회 실패"

        # 템플릿에 데이터 전달
        return render_template(
            "mypage.html",
            user_id=user_id,
            user_name=user_name,
            user_contact=user_contact
        )
    return "Unauthorized", 401

# 회원가입 API
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    id = data['id']
    password = data['password']
    name = data['name']
    contact = data['contact']

    cursor.execute("SELECT * FROM user WHERE ID = %s", (id,))
    if cursor.fetchone():
        return jsonify({"success": False, "message": "이미 존재하는 ID입니다."}), 400
    try:
        cursor.execute(
            "INSERT INTO user (ID, Password, Name, Contact) VALUES (%s, %s, %s, %s)",
            (id, password, name, contact)
        )
        db.commit()
        return jsonify({"success": True, "message": "회원가입 성공!"})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"success": False, "message": f"회원가입 실패: {err}"}), 500

# 로그인 API
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id = data['id']
    password = data['password']

    try:
        cursor.execute("SELECT ID, Name FROM user WHERE ID = %s AND Password = %s", (id, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session.permanent = True  # 세션 만료 시간 설정
            app.logger.info(f"로그인 성공: user_id={user[0]}, user_name={user[1]}")
            return jsonify({"success": True, "message": "로그인 성공!"})
        else:
            app.logger.warning("로그인 실패: 잘못된 ID 또는 비밀번호")
            return jsonify({"success": False, "message": "ID 또는 비밀번호가 일치하지 않습니다."}), 401
    except Exception as e:
        app.logger.error(f"로그인 엔드포인트에서 오류 발생: {e}")
        return jsonify({"success": False, "message": "서버 오류 발생"}), 500

# 로그아웃 API
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return jsonify({"success": True, "message": "로그아웃 성공!"})

# 로그인 상태 확인 API
@app.route('/check_login', methods=['GET'])
def check_login():
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            cursor.execute("SELECT Contact FROM user WHERE ID = %s", (user_id,))
            contact_result = cursor.fetchone()
            user_contact = contact_result[0] if contact_result else "알 수 없음"
            app.logger.info(f"로그인 상태 확인: user_id={user_id}, user_name={session['user_name']}, user_contact={user_contact}")
            return jsonify({
                "logged_in": True,
                "user_name": session['user_name'],
                "user_contact": user_contact
            })
        app.logger.warning("로그인 상태 확인: 세션이 없습니다.")
        return jsonify({"logged_in": False})
    except Exception as e:
        app.logger.error(f"check_login 엔드포인트에서 오류 발생: {e}")
        return jsonify({"logged_in": False, "error": str(e)}), 500

# 기기 제어 API
@app.route("/light", methods=['POST'])
def toggle_light():
    data = request.get_json()
    print("조명 상태 변경:", data)
    return "ok"

@app.route("/air", methods=['POST'])
def toggle_air():
    data = request.get_json()
    print("에어컨 상태 변경:", data)
    return "ok"

@app.route("/valueSave", methods=['POST'])
def save_air_settings():
    data = request.get_json()
    print("에어컨 설정 저장:", data)
    return "ok"

@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)