from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash
import config
import sqlite3
import posts

app = Flask(__name__)
app.secret_key = config.secret_key

def query(sql, *parameters):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(sql, parameters)
        return cursor.fetchall()

def database_init():
    with sqlite3.connect('database.db') as db:
        queries = [('''CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               username TEXT UNIQUE,
               password_hash TEXT)
              '''),
              ('''CREATE TABLE IF NOT EXISTS analysis (
               id INTEGER PRIMARY KEY,
               title TEXT,
               user_id INTEGER REFERENCES users)
              '''),
              ('''CREATE TABLE IF NOT EXISTS comments (
               id INTEGER PRIMARY KEY,
               content TEXT,
               sent_at TEXT,
               user_id INTEGER REFERENCES users,
               analysis_id INTEGER REFERENCES analysis)
              ''')
              ]
        for q in queries:
            query(q)

database_init()

@app.route("/")
def index():
    post_list = posts.get_posts()
    return render_template("index.html", post_list = post_list)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    
    sql = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = query(sql, username)

    if not password_hash:
        return '''VIRHE: väärä tunnus tai salasana
        <p>
        <a href='/'>
            <button>Takaisin etusivulle</button>
        </a>
        </p>
        '''
    
    password_hash = password_hash[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")