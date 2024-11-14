from flask import Flask, jsonify, request, session, logging
import mysql.connector
#from flask_cors import CORS

app = Flask(__name__)
app.secret_key = '12345678'
#CORS(app, origins=["https://mega-giants.click"])

logging.basicConfig(filename='flask.log', level=logging.INFO, format='%(asctime)s %(message)s')

db = mysql.connector.connect(
    host="user.c5keiyccyg3f.ap-northeast-2.rds.amazonaws.com",
    user="root",  # MySQL 사용자명
    password="12345678",  # MySQL 비밀번호
    database="user"  # 사용 중인 데이터베이스
)

cursor = db.cursor()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    id = data['id']
    password = data['password']
    name = data['name']
    contact = data['contact']

    cursor.execute("SELECT * FROM user WHERE ID = %s", (id,))
    existing_user = cursor.fetchone()
    if existing_user:
        return jsonify({"message": "이미 존재하는 ID입니다. 다른 ID를 사용해주세요."}), 400
    try:
        cursor.execute("INSERT INTO user (ID, Password, Name, Contact) VALUES (%s, %s, %s, %s)", 
                   (id, password, name, contact))
        db.commit()
        return jsonify({"message": "회원가입 완료!"})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"message": f"회원가입 실패: {err}"}), 500
        
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id = data['id']
    password = data['password']
    # MySQL에서 사용자 정보 조회
    cursor.execute("SELECT * FROM user WHERE ID = %s AND Password = %s", (id, password))
    user = cursor.fetchone()

    if user:
        # 세션에 사용자 ID와 이름 저장
        session['user_id'] = user[0]  # ID
        session['user_name'] = user[2]  # Name
        return jsonify({"success": True, "message": "로그인 성공!"})
    else:
        return jsonify({"success": False, "message": "ID 또는 비밀번호가 일치하지 않습니다."})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)  # 세션에서 사용자 정보 제거
    session.pop('user_name', None)
    return jsonify({"message": "로그아웃 되었습니다."})

@app.route('/check_login', methods=['GET'])
def check_login():
    # 세션에 사용자 정보가 있으면 로그인된 상태
    if 'user_id' in session:
        return jsonify({"logged_in": True, "user_name": session['user_name']})
    else:
        return jsonify({"logged_in": False})

@app.get('/')
def root():
    print("IoT기기 작동 감지")
    return "IoT기기 작동 감지"

@app.route("/light",methods=['POST'])
def productLight():
    params = request.get_json()
    if(params): print("조명  켜짐")
    else: print("조명 꺼짐")
    return "ok"

@app.route("/air",methods=['POST'])
def productAir():
    params = request.get_json()
    if(params): print("에어컨  켜짐")
    else: print("에어컨 꺼짐")
    return "ok"

@app.route("/valueSave",methods=['POST'])
def productAirSave():
    params = request.get_json()
    print(params)
    return "ok"

@app.route("/login",methods=['POST'])
def productLogin():
    params = request.get_json()
    print(params, "님이 로그인했습니다.")
    return "ok"

@app.route("/signup",methods=['POST'])
def productSingUp():
    params = request.get_json()
    print("님이 회원가입되었습니다. 사용자 정보 => " , params)
    return "ok"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1212)