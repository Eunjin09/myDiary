from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

from datetime import datetime

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.kdc5v.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta_pjt_mypicDiary_test

#### 페이지 불러오기 ####

## 일기 상세보기 페이지
@app.route('/diary/<page_num>')
def diary_view(page_num):
    # 주소 /diary/뒤의 숫자를 page_num으로 받아와서 DB의 diary에서 diary_num이 page_num과 일치하는 일기를 가져온다
    diary_data = db.diary.find_one({'diary_num':int(page_num)})

    # DB의 comment에서 diary_num이 page_num과 일치하는 코멘트들을 모두 가져온다.
    diary_comment = list(db.comment.find({'diary_num':int(page_num)}))

    return render_template('diary.html', page_num = page_num, diary_data = diary_data, diary_comment = diary_comment)


#### 여기부터 기능 API ####

## 코멘트 작성 API
@app.route('/diary/comment', methods=['POST'])
def save_comment():
    # 입력된 코멘트와, 현재 페이지의 일기 번호(diary_num)을 가져온다
    comment_receive = request.form['comment_give']
    diary_num_receive = request.form['diary_num_give']

    # 새로운 코멘트에 부여할 코멘트번호(comment_num)를 만든다
    comment_count = list(db.comment.find({}, {'_id': False}))
    comment_num = len(comment_count) + 1
    writtenTime = datetime.now()

    # 코멘트에 저장되는 정보 : 일기번호, 코멘트번호, 코멘트내용, 작성자닉네임, 작성날짜
    newComment = {
        'diary_num' : int(diary_num_receive),
        'comment_num':comment_num,
        'comment': comment_receive,
        'nickname' : '임시이름',
        'comment_date' : writtenTime.strftime('%Y-%m-%d  %H:%M')
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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)