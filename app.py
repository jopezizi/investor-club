from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import sqlite3
import posts, users

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
              ('''CREATE TABLE IF NOT EXISTS posts (
               id INTEGER PRIMARY KEY,
               title TEXT,
               content TEXT,
               sent_at TEXT,
               user_id INTEGER REFERENCES users,
               likes INTEGER,
               buys INTEGER,
               sells INTEGER)
              '''),
              ('''CREATE TABLE IF NOT EXISTS comments (
               id INTEGER PRIMARY KEY,
               content TEXT,
               sent_at TEXT,
               user_id INTEGER REFERENCES users,
               post_id INTEGER REFERENCES post)
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
    
    sql = "SELECT password_hash, id FROM users WHERE username = ?"
    user_info = query(sql, username)

    if not user_info:
        return '''VIRHE: väärä tunnus tai salasana
        <p>
        <a href='/'>
            <button>Takaisin etusivulle</button>
        </a>
        </p>
        '''
    
    password_hash = user_info[0][0]
    user_id = user_info[0][1]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = user_id
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    with sqlite3.connect('database.db') as db:
        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except sqlite3.IntegrityError:
            return "VIRHE: tunnus on jo varattu"

    return '''Tunnus luotu. Voit kirjautua sisään etusivulla.
            <p>
        <a href='/'>
            <button>Takaisin etusivulle</button>
        </a>
        </p>'''

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_id", None)
    return redirect("/")

@app.route('/new_post', methods=['POST'])
def new_post():
    if 'user_id' not in session:
        return redirect('/')
    
    title = request.form['title']
    content = request.form['content']
    user_id = session['user_id']

    post_id = posts.add_post(title, content, user_id)
    return redirect('/post/' + str(post_id))

@app.route('/post/<int:post_id>')
def show_post(post_id):
    post = posts.get_post(post_id)
    comments = posts.get_comments(post_id)
    return render_template('post.html', post=post, comments=comments)


@app.route('/search')
def search():
    query = request.args.get('query')
    results = posts.search(query) if query else []
    print(results)
    return render_template('search.html', query=query, results=results)

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_message(post_id):
    to_edit = posts.get_post(post_id)
    if isinstance(to_edit, list) and to_edit:
        post = to_edit[0]
    
    if request.method == "GET":
        return render_template("edit.html", post=post)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        posts.update_post(post["id"], title, content)
        return redirect("/post/" + str(post["id"]))

    return redirect("/")

@app.route("/remove/<int:post_id>", methods=["GET", "POST"])
def remove_message(post_id):
    to_remove = posts.get_post(post_id)
    if isinstance(to_remove, list) and to_remove:
        post = to_remove[0]

    if request.method == "GET":
        return render_template("remove.html", post=post)
    
    if request.method == "POST":
        if "continue" in request.form:
            posts.remove_post(post["id"])
        return redirect("/")
    
    return redirect("/")

@app.route("/profile/<int:user_id>", methods=['GET', 'POST'])
def profile(user_id):
    prof = users.get_user(user_id)
    if request.method == 'GET':
        return render_template('profile.html', profile=prof)
    return redirect('/')