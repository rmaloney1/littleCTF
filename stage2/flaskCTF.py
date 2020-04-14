from flask import Flask, request, redirect, url_for, make_response, render_template, render_template_string
from peewee import SqliteDatabase
from hashlib import md5
from random import choice
from string import ascii_uppercase as a_upper, ascii_lowercase as a_lower
import yaml
import os

from setup import flags, other_users

db = SqliteDatabase('level2.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = "FLAG_1_" + flags[1]

def login(username, password):
    phash = md5(password.encode('utf-8')).hexdigest()
    print("username is", username)
    qr = f"SELECT username FROM user WHERE username = ? and phash = ?"
    print("qry is", qr)
    cursor = db.execute_sql(qr, (username, phash))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        return user[0]

def auth():
    if 'username' not in request.cookies or 'sessionKey' not in request.cookies:
        return None
    username = request.cookies.get('username')
    sessionKey = request.cookies.get('sessionKey')
    cursor = db.execute_sql("SELECT username FROM sessions WHERE username = ? and sessionKey = ?", (username, sessionKey))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        return user[0]

def display_home(username):
    return render_template('search.html', username=username)

def failed_login():
    # perhaps in future display message showing login failed
    return redirect(url_for('login_endpoint'))

def failed_register():
    # perhaps in future display message showing register failed
    return redirect(url_for('login_endpoint'))

@app.route("/login", methods=["POST", "GET"])
def login_endpoint():
    if request.method == "GET":
        username = auth()
        if username:
            return redirect(url_for('home'))
        return render_template('index.html')
    else:
        if 'username' not in request.form or 'password' not in request.form:
            return failed_login()
        username = login(request.form.get('username'), request.form.get('password'))
        if not username:
            return failed_login()
        response = make_response(display_home(username))
        sessionKey = ''.join(choice(a_upper + a_lower) for _ in range(10))
        db.execute_sql('''
            INSERT OR REPLACE INTO sessions(username, sessionKey)
            VALUES(?, ?)
        ''', (username, sessionKey))
        response.set_cookie('username', username)
        response.set_cookie('sessionKey', sessionKey)
        return response

@app.route("/logout", methods=["POST"])
def logout():
    username = auth()
    if not username:
        return redirect(url_for("home"))
    
    db.execute_sql('''
        DELETE FROM sessions
        WHERE username = ?
    ''',(username,))
    return redirect(url_for("home"))

@app.route("/", methods=["GET"])
def home():
    username = auth()
    return display_home(username)


@app.route("/report", methods=["POST"])
def report():
    username = auth()
    if not username:
        return redirect(url_for("home"))
    if 'accused' in request.form:
        print("reporting", request.form.get('accused'))
    return(redirect(url_for('home')))

def badSanitise(term):
    blacklist = ["select", "union", "from", "where"]
    for i in blacklist:
        term = term.replace(i, "")
    return term

@app.route('/search/results', methods=["POST"])
def searchDB():
    
    print(request.form)
    term = request.form.get('search')
    if not term:
        return redirect(url_for('home'))
    cmd = f'''
        SELECT * FROM flights
        WHERE flights.code LIKE '{'%' + term + '%'}' '''
    print("cmd is", cmd)
    cursor = db.execute_sql(cmd)
    rows = cursor.fetchall()
    print(rows, term)
    term = badSanitise(term)
    string = '''{% extends "layout.html" %}
        {% block title %} Search Results {% endblock %}
        {% block content %}
        <h1>Search Results for ''' + term + "</h1>" # SSTI vulnerability (and XSS)
    with open("templates/searchResults.html") as f:
        string += f.read()
    return render_template_string(string, rows=rows)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() == "yaml"

@app.route("/upload", methods=["POST"])
def uploadFile():
    print(request.form)
    print(request.files)
    if 'flightfile' not in request.files:
        return redirect(url_for('home'))
    file = request.files['flightfile']
    text = file.read()

    if not allowed_file(file.filename):
        return redirect(url_for('home'))

    stuff = yaml.unsafe_load(text)
    print(stuff)

    for flight in stuff:
        reqs = ['code', 'airline', 'from', 'to', 'deptTime', 'arriveTime']
        for i in reqs:
            if i not in flight:
                print(i)
                return "Error, incorrect structure. Please inlucde: code, airline, from, to, depttime, arriveTime for each flight"
        code = flight['code']
        airline = flight['airline']
        departsFrom = flight['from']
        goingTo = flight['to']
        departTime = flight['deptTime']
        arriveTime = flight['arriveTime']
        db.execute_sql('''
            INSERT INTO flights (code, airline, departsFrom, goingTo, departTime, arriveTime)
            VALUES (?, ?, ?, ?, ?, ?)
        ''',(code, airline, departsFrom, goingTo, departTime, arriveTime))
    
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(port=5001)