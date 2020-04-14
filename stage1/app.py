from flask import Flask, request, redirect, url_for, make_response, render_template
from peewee import SqliteDatabase
from hashlib import sha256
from random import choice
from string import ascii_uppercase as a_upper, ascii_lowercase as a_lower

from setflags import flags, other_users

db = SqliteDatabase('level1.db')

app = Flask(__name__)

def flag1(id):
    cursor = db.execute_sql('''
        SELECT author FROM blogs WHERE id = ?
    ''',(id,))
    post = cursor.fetchone()
    if post and post[0] in other_users:
        return True
    return False

def flag2(username):
    if username in other_users:
        return True
    return False

def sanitise(text):
    outp = ""
    for letter in text:
        if letter == "'":
            outp += "'"
        outp += letter
    return outp

def login(username, password):
    phash = sha256(password.encode('utf-8')).hexdigest()
    #username = sanitise(username)
    print("username is", username)
    qr = f"SELECT username FROM user WHERE username = '{username}' and phash = ?"
    print("qry is", qr)
    cursor = db.execute_sql(qr, (phash,))
    user = cursor.fetchone()
    if user is None:
        return False
    else:
        return user[0]

def register(username, password):
    phash = sha256(password.encode('utf-8')).hexdigest()

    cursor = db.execute_sql("SELECT username FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user is not None:
        print(cursor.fetchall())
        return False
    else:
        cursor = db.execute_sql("INSERT INTO user (username, phash) VALUES(?, ?)", (username,phash))
        return username

def auth():
    if 'username' not in request.cookies or 'sessionKey' not in request.cookies:
        return False
    username = request.cookies.get('username')
    sessionKey = request.cookies.get('sessionKey')
    cursor = db.execute_sql("SELECT username FROM sessions WHERE username = ? and sessionKey = ?", (username, sessionKey))
    user = cursor.fetchone()
    if user is None:
        return False
    else:
        return user[0]

def display_home(username):
    cursor = db.execute_sql('''
        SELECT author, title, id from blogs
        WHERE privacy = 0
        OR author = ?
    ''',(username,))
    rows = cursor.fetchall()
    print("displaying home with", rows)
    flag = ""
    flag2_found = False
    if flag2(username):
        flag2_found = True
        flag = "FLAG_2_" + flags[2]
    return render_template('searchResults.html', username=username, rows=rows, flag2=flag2_found, flag=flag)

def failed_login():
    return redirect(url_for('index'))
def failed_register():
    return redirect(url_for('index'))

@app.route("/", methods=["GET"])
def index():
    username = auth()
    if username:
        return redirect(url_for('home'))
    
    return render_template('index.html')


@app.route("/login", methods=["POST"])
def login_endpoint():
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
        return redirect(url_for("index"))
    
    db.execute_sql('''
        DELETE FROM sessions
        WHERE username = ?
    ''',(username,))
    return redirect(url_for("index"))

@app.route("/register", methods=["POST"])
def register_endpoint():
    print("register appempt")
    if 'username' not in request.form or 'password' not in request.form:
        print('something missing', request.form)
        return failed_register()
    username = register(request.form.get('username'), request.form.get('password'))
    if not username:
        print('registration not unique', username)
        return failed_register()
    response = make_response(display_home(username))
    sessionKey = ''.join(choice(a_upper + a_lower) for _ in range(10))
    db.execute_sql('''
        INSERT OR REPLACE INTO sessions(username, sessionKey)
        VALUES(?, ?)
    ''', (username, sessionKey))
    response.set_cookie('username', username)
    response.set_cookie('sessionKey', sessionKey)
    return response

@app.route("/home", methods=["GET"])
def home():
    username = auth()
    if not username:
        return redirect(url_for("index"))
    return display_home(username)

@app.route("/create", methods=["GET", "POST"])
def create():
    username = auth()
    if not username:
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template('create.html')
    else:
        args = ['title', 'content']
        if any(i not in request.form for i in args):
            print('something missing', request.form)
            return render_template('create.html')
        title = request.form.get('title')
        content = request.form.get('content')
        privacy = 'privacy' in request.form
        db.execute_sql('''
            INSERT INTO blogs(author, title, privacy, content)
            VALUES (?, ?, ?, ?)
        ''',(username, title, privacy, content))
        return redirect(url_for('home'))

@app.route("/report", methods=["POST"])
def report():
    username = auth()
    if not username:
        return redirect(url_for("index"))
    if 'accused' in request.form:
        print("reporting", request.form.get('accused'))
    return(redirect(url_for('home')))

@app.route("/view/<id>", methods=["GET"])
def view(id):
    username = auth()
    if not username:
        return redirect(url_for("index"))
    
    # forget to check that private pages should be only viewable by their author

    cursor = db.execute_sql('''
        SELECT author, title, content FROM blogs
        WHERE id = ?
    ''',(id,))
    post = cursor.fetchone()
    if post is None:
        return redirect(url_for("home"))
    
    return render_template('view.html', author=post[0], title=post[1], content=post[2])



@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "GET":
        username = auth()
        if not username:
            return redirect(url_for("index"))
        cursor = db.execute_sql('''
            SELECT author, title, content, privacy, id FROM blogs
            WHERE id = ?
        ''',(id,))
        post = cursor.fetchone()
        if post is None:
            resp = make_response("post not found", 404)
            return resp
        if post[0] != username:
            return make_response("This is someone else's post!", 403)
        return render_template('edit.html', title=post[1], content=post[2], privacy=post[3], id=post[4])

    else:
        # this is vulnerable, does not authenticate sender
        args = ['title', 'content']
        if any(i not in request.form for i in args):
            return redirect(url_for('home'))
        privacy = 'privacy' in request.form
        title = request.form.get('title')
        if flag1(id):
            title = "FLAG_1_" + flags[1]

        content = request.form.get('content')
        db.execute_sql('''UPDATE blogs
            SET title = ?, content = ?, privacy = ?
            WHERE id = ?
        ''',(title, content, privacy, id))
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()