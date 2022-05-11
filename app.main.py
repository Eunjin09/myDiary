from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests


app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.kdc5v.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta_pjt_mypicDiary_test


def loginCheck():
    if request.cookies.get('mytoken') is not None:
        return True
    else:
        return False

##메인페이지
@app.route('/')
def main():
    all_list = list(db.diary.find({},{'_id':False}))
    return render_template("mainpage.html", all_list=all_list, loginCheck=loginCheck )

##상세페이지
@app.route('/diary/<page_num>')
def diary_view(page_num):

    return render_template('diary.html', page_num=page_num)

##작성하기
@app.route('/write')
def write():

    return render_template('write.html')




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


