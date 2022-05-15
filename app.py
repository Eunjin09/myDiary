from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

import datetime
import jwt
import hashlib
import certifi

SECRET_KEY = 'CLAW'

#### MongoClient 각자 자기 코드 넣어서 테스트 하기!! ####
from pymongo import MongoClient
client = MongoClient('')
db = client.dbsparta_pjt_mypicDiary_test


def loginCheck():
    if request.cookies.get('mytoken') is not None:
        return True
    else:
        return False

#### 페이지 불러오기 ####

##메인페이지
@app.route('/')
def main():
    all_list = list(db.diary.find({}, {'_id': False}))
    return render_template("mainpage.html", all_list=all_list, loginCheck=loginCheck())

##일기 작성 페이지
@app.route('/post')
def diary_post():
    return render_template('post.html')


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')


@app.route('/sign_up/check_dup')
def check_dup():
    return render_template('sign_up.html')



## 일기 상세보기 페이지
@app.route('/diary/<page_num>')
def diary_view(page_num):
    # 주소 /diary/뒤의 숫자를 page_num으로 받아와서 DB의 diary에서 diary_num이 page_num과 일치하는 일기를 가져온다
    diary_data = db.diary.find_one({'diary_num': int(page_num)})

    # DB의 comment에서 diary_num이 page_num과 일치하는 코멘트들을 모두 가져온다.
    diary_comment = list(db.comment.find({'diary_num': int(page_num)}))

    return render_template('diary.html', page_num=page_num, diary_data=diary_data, diary_comment=diary_comment)




## 일기 작성 API
@app.route('/post', methods=['POST'])
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
        return jsonify({'result': 'success', 'msg': '일기 저장 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

## 코멘트 작성 API
@app.route('/diary/comment', methods=['POST'])
def save_comment():
    # 입력된 코멘트와, 현재 페이지의 일기 번호(diary_num)을 가져온다
    comment_receive = request.form['comment_give']
    diary_num_receive = request.form['diary_num_give']

    # 새로운 코멘트에 부여할 코멘트번호(comment_num)를 만든다
    comment_count = list(db.comment.find({}, {'_id': False}))
    comment_num = len(comment_count) + 1

    # 코멘트에 저장되는 정보 : 일기번호, 코멘트번호, 코멘트내용, 작성자닉네임, 작성날짜
    newComment = {
      'diary_num': int(diary_num_receive),
      'comment_num': comment_num,
      'comment': comment_receive,
      'nickname': '임시이름',
      'comment_date': "2022-05-12"
    }

    db.comment.insert_one(newComment)

    return jsonify({'msg': '코멘트 등록 완료!'})


## 일기추천 API
@app.route('/diary/recommend', methods=['POST'])
def post_recommend():
    # 현재 페이지의 일기번호(diary_num)와, 일기번호에 해당하는 일기의 추천수(recommend_count)를 받아온다
    diary_num_receive = request.form['diary_num_give']
    recommend_count_receive = request.form['recommend_count_give']

    #일기 추천수를 +1 해준다
    recommend_count = int(recommend_count_receive) + 1

    # DB에서 일치하는 일기번호의 추천수를 업데이트한다
    db.diary.update_one({'diary_num': int(diary_num_receive)}, {'$set': {'recommendCount': recommend_count}})

    return jsonify({'msg':'일기장 추천완료!'})

## 일기 신고 API
@app.route('/diary/report', methods=['POST'])
def post_report():
    # 현재 페이지의 일기번호(diary_num)와, 일기번호에 해당하는 일기의 신고횟수(report_count)를 받아온다
    diary_num_receive = request.form['diary_num_give']
    report_count_receive = request.form['report_count_give']

    # 일기 신고횟수를 +1 해준다
    report_count = int(report_count_receive) + 1
    print(report_count)

    # DB에서 일치하는 일기번호의 신고횟수를 업데이트한다
    db.diary.update_one({'diary_num': int(diary_num_receive)}, {'$set': {'reportCount': report_count}})

    return jsonify({'msg':'일기장이 신고되었습니다. 불편드려 죄송합니다.'})



#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/sign_up', methods=['POST'])
def api_sign_up():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name': name_receive})

    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def api_check_dup():
    id_receive = request.form['id_give']
    exists = bool(db.user.find_one({'id': id_receive},{'_id': 0}))
    return jsonify({'result': 'success', 'exists': exists})



# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24),

        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/', methods=['POST'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'name': userinfo['name']})


    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
