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
Image = ["img/Snipaste_2024-08-05_19-26-00.png","img/Snipaste_2024-08-05_19-34-38.png","img/Snipaste_2024-08-05_20-00-47.png", "img/Snipaste_2024-08-05_20-01-22.png"]
# data = [{"name ":"name1", "category":"category1","img_src":["img1","img2","img3"], "open":"time1", "description":"info1"}]
data = list(db.stores.find({},{'_id':0}))

@app.route('/')
def home():
    state = True
    token_receive = request.cookies.get('mytoken')
    review_data = list(db.Review.find({},{'_id':0}))
    if token_receive == None:
        return render_template('index2.html', state=state, image1=Image[0],image2=Image[1],image3=Image[2],image4=Image[3],data=data,review_data=review_data)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.Account.find_one({"Id": payload['id']})
        return render_template('index2.html',state=state, nickname=user_info["nickname"],image1=Image[0],image2=Image[1],image3=Image[2],image4=Image[3],data=data,review_data=review_data)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지않습니다."))

@app.route('/details/<name>')
def details(name):
    state = False
    store_name=name
    token_receive = request.cookies.get('mytoken')
    review_data = list(db.Review.find({},{'_id':0}))
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        Id_info = payload['id']
        user_info = db.Account.find_one({"Id": payload['id']})
        store = next((item for item in data if item['name'] == name), None)
        if store:
           return render_template('index2.html', state=state , store_name=store_name, data=data, Id_info=Id_info,nickname=user_info["nickname"],review_data=review_data)
        else:
            return redirect(url_for('home'))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지않습니다."))

# @app.route('/review')
# def review():
#     return render_template('store.html') 

@app.route('/api/postreview', methods=['POST'])
def post_review():
    review_receive = request.form['review_give']
    score_receive = request.form['score_give']
    Id_receive = request.form['Id_give']
    nickname_receive = request.form['nickname_give']
    store_name_receive = request.form['storename_give']
    review_list = {'Id' : Id_receive, 'store_name' : store_name_receive, 'nickname': nickname_receive, 'review':review_receive, 'score':score_receive}
    result = db.Review.insert_one(review_list)
    if result:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})

    

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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail'}) 

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

    