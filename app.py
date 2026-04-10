from flask import *
from werkzeug.security import check_password_hash, generate_password_hash
import config
import sqlite3
import db
import posts, users

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if 'user_id' not in session:
        abort(403)

@app.route("/")
def index():
    post_list = posts.get_posts()
    return render_template("index.html", post_list = post_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', error=None)

    return redirect('/register')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html', error=None)
    
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    
    sql = "SELECT password_hash, id FROM users WHERE username = ?"
    user_info = db.query(sql, [username])

    if not user_info:
        return render_template('login.html', error="Väärä tunnus tai salasana")
    
    password_hash = user_info[0][0]
    user_id = user_info[0][1]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = user_id
        return redirect("/")
    else:
        return render_template('login.html', error="Väärä tunnus tai salasana")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    
    if password1 != password2:
        return render_template('register.html', error="Salasanat eivät ole samat")
    
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, datetime('now', 'localtime'))"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return render_template('register.html', error="Tunnus on jo varattu")

    return render_template('register.html', error=None, success="Tunnus luotu! Voit kirjautua sisään.")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_id", None)
    return redirect("/")

@app.route('/new_post')
def new_post():
    require_login()

    return render_template('new_post.html')

@app.route('/create_post', methods=['POST'])
def create_post():
    require_login()
    
    if not users.get_user(session['user_id']):
        session.pop('username', None)
        session.pop('user_id', None)
        return redirect('/login')
    
    title = request.form['title']
    content = request.form['content']
    market = request.form['market']
    industry = request.form['industry']
    strategy = request.form['strategy']
    recommendation = request.form['recommendation']
    if not title or not content or len(title) > 100 or len(content) > 5000:
        abort(403)
    user_id = session['user_id']
    post_id = posts.add_post(title, content, user_id, market, industry, strategy, recommendation)
    return redirect('/post/' + str(post_id))

@app.route('/post/<int:post_id>')
def show_post(post_id):
    post = posts.get_post(post_id)
    liked = False
    current_recommendation = None
    if 'user_id' in session:
        user_id = session['user_id']
        liked = bool(posts.get_user_liked(user_id, post_id))
        recommended = posts.get_user_recommended(user_id, post_id)
        current_recommendation = recommended[0]['recommendation'] if recommended else None
    if not post:
        abort(404)
    comments = posts.get_comments(post_id)
    return render_template('post.html', post=post, comments=comments, liked=liked, current_recommendation=current_recommendation)


@app.route('/search')
def search():
    query = request.args.get('query')
    results = posts.search(query) if query else []
    return render_template('search.html', query=query, results=results)

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_message(post_id):
    require_login()
    
    if not users.get_user(session['user_id']):
        session.pop('username', None)
        session.pop('user_id', None)
        return redirect('/login')
    
    post = posts.get_post(post_id)
    if not post:
        abort(404)
    
    if post['user_id'] != session['user_id']:
        abort(403)
    
    if request.method == "GET":
        return render_template("edit.html", post=post)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        posts.update_post(post["id"], title, content)
        return redirect("/post/" + str(post["id"]))

    return redirect('/')

@app.route("/remove/<int:post_id>", methods=["GET", "POST"])
def remove_message(post_id):
    require_login()

    if not users.get_user(session['user_id']):
        session.pop('username', None)
        session.pop('user_id', None)
        return redirect('/login')
    
    post = posts.get_post(post_id)
    if not post:
        abort(404)

    if post['user_id'] != session['user_id']:
        abort(403)
    
    if request.method == "GET":
        return render_template("remove.html", post=post)
    
    if request.method == "POST":
        if "continue" in request.form:
            posts.remove_post(post["id"])
        return redirect("/")
    
    return redirect("/")

@app.route("/profile/<int:user_id>")
def profile(user_id):
    prof = users.get_user(user_id)
    if not prof:
        abort(404)
    posts = users.get_posts(user_id)
    return render_template('profile.html', profile=prof, posts=posts)

@app.route("/add_profile_picture", methods = ["GET", "POST"])
def add_profile_picture():
    require_login()

    if request.method == 'GET':
        return render_template('add_profile_picture.html', error = None)
    
    if request.method == 'POST':
        file = request.files['image']
        if not file.filename.endswith('.jpg'):
            return render_template('add_profile_picture.html', error = "väärä tiedostomuoto")

        image = file.read()
        if len(image) > 400 * 1024:
            return render_template('add_profile_picture.html', error = "liian suuri kuva")

        user_id = session['user_id']
        users.update_profile_picture(user_id, image)
        return redirect('/profile/'+str(user_id))        
    return redirect('/')

@app.route("/delete_profile_picture")
def delete_profile_picture():
    require_login()

    user_id = session['user_id']
    users.delete_profile_picture(user_id)
    return redirect('/profile/' + str(user_id))

@app.route('/pfp/<int:user_id>')
def show_image(user_id):
    pfp = users.get_profile_picture(user_id)
    if not pfp:
        abort(404)
    response = make_response(bytes(pfp[0]))
    response.headers.set('Content-Type', 'image/jpeg')
    return response

@app.route('/post/<int:post_id>/toggle-like', methods=['POST'])
def toggle_like(post_id):
    require_login()
    user_id = session['user_id']
    liked = posts.get_user_liked(user_id, post_id)
    if liked:
        posts.delete_like(user_id, post_id)
        liked = False
    else:
        posts.add_like(user_id, post_id)
        liked = True
    return redirect('/post/' + str(post_id))
    

@app.route('/post/<int:post_id>/update-recommendation', methods=['POST'])
def update_recommendation(post_id):
    require_login()
    user_id = session['user_id']
    recommended = posts.get_user_recommended(user_id, post_id)
    recommendation = request.form['recommendation']
    posts.update_recommendation(user_id, post_id, recommended, recommendation)
    return redirect('/post/' + str(post_id))