# -*- coding:utf-8 -*-
import json
from flask import Flask, Response, session
from flask import request, redirect, url_for
from flask import make_response, render_template

app = Flask(__name__, static_folder='static', static_url_path='/static')
# 给session设置key
app.config['SECRET_KEY'] = '123456'

#定义一个装饰器用于拦截用户登录
#func是使用该修饰符的地方是视图函数
def login_require(func):
    def decorator(*args, **kwargs):
        print(session)
        user = session.get('user')
        if user:
            return func(*args, **kwargs)
        return redirect('login')
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        if password != '111' or user == '':
            return redirect(url_for('login'))
        else:
            session['user'] = user
            return redirect(url_for('test'))
    elif request.method == 'GET':
        return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    print(session)
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/test')
# @login_require
def test():
    # if 'user' not in session:
    #     return redirect(url_for('login'))
    return render_template('test.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    print(request.headers)
    response = make_response(json.dumps({"data":"Hello Flask!"}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Access-Control-Allow-Headers"] = "X-Requested-With"  
    response.headers["Access-Control-Allow-Expose-Headers"] = "*"  
    response.headers["Access-Control-Allow-Methods"] = "PUT,POST,GET,DELETE,OPTIONS" 
    return response

@app.route('/post_test', methods=['GET', 'POST'])
def post_test():
    if request.method == 'POST':
        print(request.headers)
        print(request.data)
        print(request.form)
        # print(request.files)
        # with open ('test.jpg', 'wb') as f:
        #     f.write(request.files['file'].read())
        return Response(json.dumps({'ret': 2}), mimetype='application/json')
    elif request.method == 'GET':
        return Response(json.dumps({'err': 3}), mimetype='application/json')
        # return render_template('login.html')

@app.route('/post_file', methods=['GET', 'POST'])
def post_file():
    if request.method == 'POST':
        file = request.files['file']
        print(file.filename)
        file.save('static/{}'.format(file.filename))
        return Response(json.dumps({'ret': 2}), mimetype='application/json')
    elif request.method == 'GET':
        return render_template('post_file.html')

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 80,  
        debug = True 
    )
