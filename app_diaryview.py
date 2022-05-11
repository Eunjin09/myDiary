from flask import Flask, render_template, jsonify, request, jsonify, redirect, url_for
app = Flask(__name__)

from datetime import datetime

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.kdc5v.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta_pjt_mypicDiary_test

@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    return render_template("index.html")

## 일기 상세보기 페이지
@app.route('/diary/<page_num>')
def diary_view(page_num):
    diary_data = db.diary.find_one({'diary_num':int(page_num)})
    diary_comment = list(db.comment.find({'diary_num':int(page_num)}))

    return render_template('diary.html', page_num = page_num, diary_data = diary_data, diary_comment = diary_comment)


## 코멘트 작성 API
@app.route('/diary/comment', methods=['POST'])
def save_comment():
    comment_receive = request.form['comment_give']
    diary_num_receive = request.form['diary_num_give']

    comment_count = list(db.comment.find({}, {'_id': False}))
    comment_num = len(comment_count) + 1
    writtenTime = datetime.now()

    newComment = {
        'diary_num' : int(diary_num_receive),
        'comment_num':comment_num,
        'comment': comment_receive,
        'name' : '임시이름',
        'comment_date' : writtenTime.strftime('%Y-%m-%d  %H:%M')
    }

    db.comment.insert_one(newComment)

    return jsonify({'msg': '코멘트 등록 완료!'})


## 일기추천 API
@app.route('/diary/recommend', methods=['POST'])
def post_recommend():
    diary_num_receive = request.form['diary_num_give']
    recommend_count_receive = request.form['recommend_count_give']

    recommend_count = int(recommend_count_receive) + 1

    db.diary.update_one({'diary_num': int(diary_num_receive)}, {'$set': {'recommendCount': recommend_count}})

    return jsonify({'msg':'일기장 추천완료!'})

## 일기 신고 API
@app.route('/diary/report', methods=['POST'])
def post_report():
    diary_num_receive = request.form['diary_num_give']
    report_count_receive = request.form['report_count_give']

    report_count = int(report_count_receive) + 1
    print(report_count)

    db.diary.update_one({'diary_num': int(diary_num_receive)}, {'$set': {'reportCount': report_count}})

    return jsonify({'msg':'일기장이 신고되었습니다. 불편드려 죄송합니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)