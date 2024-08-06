from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient 
import hashlib
import datetime
import jwt

app = Flask(__name__)

client = MongoClient('mongodb+srv://eun0571:573582@cluster0.kuzvz3p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.dbjungle
SECRET_KEY = "jgwk00t3"

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.Account.find_one({"Id": payload['id']})
        return render_template('index.html', nickname=user_info["nickname"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/api/register/check', methods=['POST'])
def register_Id_check():
    Id_receive = request.form['Id_give']
    result = db.Account.find_one({'Id' : Id_receive})
    if result:
        return jsonify({'result': 'fail'})
    else:
        return jsonify({'result': 'success'})


@app.route('/api/register', methods=['POST'])
def api_register():
    Id_receive = request.form['Id_give']
    Pw_receive = request.form['Pw_give']
    nickname_receive = request.form['nickname_give']
    Pw_hash = hashlib.sha256(Pw_receive.encode('utf-8')).hexdigest()
    
    Account={'Id' : Id_receive, 'Pw' : Pw_hash, 'nickname': nickname_receive}
    result = db.Account.insert_one(Account)
    if result:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})

@app.route('/api/login', methods=['POST'])
def api_login():
    Id_receive = request.form['Id_give']
    Pw_receive = request.form['Pw_give']

    Pw_hash = hashlib.sha256(Pw_receive.encode('utf-8')).hexdigest()
    
    result = db.Account.find_one({'Id' : Id_receive, 'Pw' : Pw_hash})
    if result:
        payload = {
            'id': Id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail'}) 

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

    