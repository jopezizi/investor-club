from flask import  Flask, render_template, redirect, request, session
import sqlite3
import config
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = config.secret_key
database_file = 'database.db'

def init_database():
    with sqlite3.connect(database_file) as db:
        db.execute('''
                   CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY,
                   username TEXT UNIQUE,
                   password_hash TEXT
                   )''')
        db.commit()

init_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/create', methods=['POST'])
def create():
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    if password1 != password2:
        return 'Salasanat eivät täsmää'
    password_hash = generate_password_hash(password1)
    
    try:
        with sqlite3.connect(database_file) as db:
            sql = 'INSERT INTO users (username, password_hash) VALUES (?,?)'
            db.execute(sql, [username, password_hash])
            db.commit()
    except sqlite3.IntegrityError:
        return 'Käyttäjätunnus varattu.'
    
    return 'Käyttäjätunnus luotu.'


