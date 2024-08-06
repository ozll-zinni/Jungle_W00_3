from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient 
import hashlib

app = Flask(__name__)

client = MongoClient('mongodb+srv://eun0571:573582@cluster0.kuzvz3p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.dbjungle
@app.route('/')
def home():
   return render_template('index.html')



@app.route('/login', methods=['GET'])
def render_login():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def render_register():
    return render_template('register.html')


@app.route('/register/check', methods=['POST'])
def register_Id_check():
    Id_receive = request.form['Id_give']
    result = db.Account.find_one({'Id' : Id_receive})
    if result:
        return jsonify({'result': 'fail'})
    else:
        return jsonify({'result': 'success'})


@app.route('/register', methods=['POST'])
def register():
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

@app.route('/login', methods=['POST'])
def login():
    Id_receive = request.form['Id_give']
    Pw_receive = request.form['Pw_give']

    Pw_hash = hashlib.sha256(Pw_receive.encode('utf-8')).hexdigest()
    
    result = db.Account.find_one({'Id' : Id_receive, 'Pw' : Pw_hash})
    if result:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})

    

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

    