import secrets
import math
import time

from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session, g

import markupsafe
from werkzeug.security import check_password_hash, generate_password_hash

import config
import posts
import users

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

@app.before_request
def check_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed_time = round(time.time() - g.start_time, 2)
    print("Elapsed time:", elapsed_time, 's')
    return response

def check_csrf():
    if request.form.get('csrf_token') != session.get('csrf_token'):
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace('\n', '<br />')
    return markupsafe.Markup(content)

def require_login():
    if 'user_id' not in session:
        abort(403)

@app.context_processor
def inject_posts():
    all_posts = posts.get_posts(1,20)
    return {"all_posts": all_posts}

@app.route("/")
@app.route('/<int:page>')
def index(page=1):
    page_size = 10
    post_count = posts.post_count()
    page_count = math.ceil(post_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect('/1')
    if page > page_count:
        return redirect('/' + str(page_count))

    post_list = posts.get_posts(page, page_size)
    return render_template("index.html", page = page, page_count = page_count, post_list = post_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', error = None)

    check_csrf()

    return redirect('/register')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html', error = None)

    check_csrf()

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    user_info = users.authenticate_user(username)

    if not user_info:
        return render_template('login.html', error = "Väärä tunnus tai salasana")

    password_hash = user_info[0]
    user_id = user_info[1]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = user_id
        session['csrf_token'] = secrets.token_hex(16)
        return redirect("/")
    return render_template('login.html', error = "Väärä tunnus tai salasana")

@app.route("/create", methods = ["POST"])
def create():
    check_csrf()

    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return render_template('register.html', error = "Salasanat eivät ole samat")

    password_hash = generate_password_hash(password1)

    if users.create_user(username, password_hash):
        return render_template('register.html',
                               error = None,
                               success = "Tunnus luotu! Voit kirjautua sisään.")
    return render_template('register.html', error = "Tunnus on jo varattu")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_id", None)
    return redirect("/")

@app.route('/new_post')
def new_post():
    require_login()

    return render_template('new_post.html')

@app.route('/create_post', methods = ['POST'])
def create_post():
    require_login()
    check_csrf()

    if not users.get_user(session['user_id']):
        session.pop('username', None)
        session.pop('user_id', None)
        return redirect('/login')

    title = request.form.get('title', '')
    content = request.form.get('content', '')
    market = request.form.get('market', '')
    industry = request.form.get('industry', '')
    strategy = request.form.get('strategy', '')
    recommendation = request.form.get('recommendation', '')
    image_file = request.files.get('post_image')
    image = image_file.read() if image_file and image_file.filename else None
    if not title or not content or len(title) > 100 or len(content) > 5000:
        abort(403)
    user_id = session['user_id']
    post_id = posts.add_post(title, content, user_id, market, industry,
                             strategy, recommendation, image)
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
    return render_template('post.html', post = post, comments = comments,
                           liked = liked, current_recommendation = current_recommendation)

@app.route('/post-image/<int:post_id>')
def show_post_image(post_id):
    post = posts.get_post(post_id)
    if not post or not post['image']:
        abort(404)
    response = make_response(bytes(post['image']))
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/search')
def search():
    query = request.args.get('query')
    results = posts.search(query) if query else []
    return render_template('search.html', query = query, results = results)

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
        check_csrf()
        if 'continue' in request.form:
            title = request.form["title"]
            content = request.form["content"]
            posts.update_post(post["id"], title, content)
            return redirect("/post/" + str(post["id"]))
        if 'cancel' in request.form:
            return redirect("/post/" + str(post["id"]))

    return redirect('/')

@app.route("/edit/<int:post_id>/<int:comment_id>", methods = ["GET", "POST"])
def edit_comment(post_id, comment_id):
    require_login()

    if not users.get_user(session['user_id']):
        session.pop('username', None)
        session.pop('user_id', None)
        return redirect('/login')

    comment = posts.get_comment(post_id, comment_id)
    post = posts.get_post(post_id)
    if not comment:
        abort(404)

    if comment['user_id'] != session['user_id']:
        abort(403)

    if request.method == "GET":
        return render_template("edit_comment.html", comment = comment, post = post)

    if request.method == "POST":
        check_csrf()
        if 'continue' in request.form:
            content = request.form["content"]
            posts.update_comment(comment["id"], content)
            return redirect("/post/" + str(post_id))
        if 'cancel' in request.form:
            return redirect("/post/" + str(post_id))

    return redirect('/')


@app.route("/remove/<int:post_id>", methods = ["GET", "POST"])
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
        return render_template("remove.html", post = post)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            posts.remove_post(post["id"])
        if "cancel" in request.form:
            return redirect("/post/" + str(post_id))
        return redirect("/")

    return redirect("/")

@app.route("/remove/<int:post_id>/<int:comment_id>", methods = ["GET", "POST"])
def remove_comment(post_id, comment_id):
    require_login()

    if not users.get_user(session['user_id']):
        session.pop('username', None)
        session.pop('user_id', None)
        return redirect('/login')

    comment = posts.get_comment(post_id, comment_id)
    post = posts.get_post(post_id)
    if not comment:
        abort(404)

    if comment['user_id'] != session['user_id']:
        abort(403)

    if request.method == "GET":
        return render_template("remove_comment.html", comment = comment, post = post)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            posts.remove_comment(comment["id"])
        if "cancel" in request.form:
            return redirect("/post/" + str(post_id))
        return redirect("/post/" + str(post_id))

    return redirect("/")

@app.route("/profile/<int:user_id>")
def profile(user_id):
    prof = users.get_user(user_id)
    if not prof:
        abort(404)
    postlist = users.get_posts(user_id)
    recommendations = posts.get_recommendation_distribution(user_id)[0]
    likes = posts.get_user_total_likes(user_id)[0]
    return render_template('profile.html', profile = prof, posts = postlist,
                           recommendations = recommendations, likes = likes)

@app.route("/add_profile_picture", methods = ["GET", "POST"])
def add_profile_picture():
    require_login()

    if request.method == 'GET':
        return render_template('add_profile_picture.html', error = None)

    if request.method == 'POST':
        check_csrf()
        file = request.files.get('image')
        if not file or not file.filename:
            return render_template('add_profile_picture.html', error = "väärä tiedostomuoto")
        if not file.filename.endswith('.jpg'):
            return render_template('add_profile_picture.html', error = "väärä tiedostomuoto")

        image = file.read()
        if len(image) > 400 * 1024:
            return render_template('add_profile_picture.html', error = "liian suuri kuva")

        user_id = session['user_id']
        users.update_profile_picture(user_id, image)
        return redirect('/profile/' + str(user_id))
    return redirect('/')

@app.route("/delete_profile_picture", methods = ["POST"])
def delete_profile_picture():
    require_login()
    check_csrf()

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

@app.route('/post/<int:post_id>/toggle-like', methods = ['POST'])
def toggle_like(post_id):
    require_login()
    check_csrf()
    user_id = session['user_id']
    liked = posts.get_user_liked(user_id, post_id)
    if liked:
        posts.delete_like(user_id, post_id)
        liked = False
    else:
        posts.add_like(user_id, post_id)
        liked = True
    return redirect('/post/' + str(post_id))


@app.route('/post/<int:post_id>/update-recommendation', methods = ['POST'])
def update_recommendation(post_id):
    require_login()
    check_csrf()
    user_id = session['user_id']
    recommended = posts.get_user_recommended(user_id, post_id)
    recommendation = request.form['recommendation']
    posts.update_recommendation(user_id, post_id, recommended, recommendation)
    return redirect('/post/' + str(post_id))

@app.route('/categories', methods = ['GET'])
def categories():
    classes = posts.get_classes()
    categories_list = []
    for i, class_item in enumerate(classes): # pyright: ignore[reportArgumentType]
        categories_list.append([])
        items = posts.get_category_items(class_item[0])
        for cat in items:
            categories_list[i].append(cat)
    if request.method == 'GET':
        return render_template('categories.html', classes = classes, categories = categories_list)
    return render_template('categories.html', classes = classes, categories = categories_list)

@app.route('/categories/<int:category_id>', methods=['GET'])
def show_category(category_id):
    info = posts.get_category_info(category_id)[0]
    class_name, cat_name = info[0], info[1]
    post_list = posts.get_posts_by_category(class_name, cat_name)
    return render_template('show_category.html', category = cat_name, post_list = post_list)

@app.route('/new_comment', methods=['POST'])
def new_comment():
    check_csrf()
    content = request.form['content']
    user_id = session['user_id']
    post_id = request.form['post_id']

    posts.add_comment(content, user_id, post_id)
    return redirect('/post/' + str(post_id))
