from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient


import certifi
import jwt
import datetime
import hashlib

client = MongoClient('mongodb+srv://sparta:test@cluster0.gqkk6.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=certifi.where())
# client = MongoClient('내AWS아이피', 27017, username="아이디", password="비밀번호")
db = client.dbdiary

SECRET_KEY = 'CLAW'



@app.route('/')
def home():

    return render_template('index.html')



@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    return jsonify({'result': 'success'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 회원가입
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # DB에 저장
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # ID 중복확인
    return jsonify({'result': 'success'})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 프로필 업데이트
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/post', methods=['GET','POST'])
def post():

    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰을 넘겨주지않아도 항상 쿠키로 토큰을 가져올 수 있다
        # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id ": payload['id']})
        print(user_info)
        user_info = db.users.find_one({"username": payload["id"]})

        # 포스팅하기
        image_receive = request.form["image"]
        nickname_receive = request.form["nickname"]
        title_receive = request.form["title"]
        date_receive = request.form["diary_date"]
        weather_receive = request.form["weather"]
        texts_receive = request.form["texts"]

        # num 가져오기
        diary_list = list(db.diary.find({}, {'_id': False}))
        count = len(diary_list) + 1
        doc = {
            'diary_num' : count,
            'image': image_receive,
            'nickname': nickname_receive,
            'title': title_receive,
            'diary_date': date_receive,
            'weather': weather_receive,
            'texts': texts_receive,
            'recommendCount': "0",
            'reportCount': "0"
        }

        db.diary.insert_one(doc)
        myname = "작성 완료!"
        return render_template("post.html", msg=myname)
        # return redirect(url_for("post", msg="작성 완료!"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅 목록 받아오기
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다."})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        return jsonify({"result": "success", 'msg': 'updated'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)




