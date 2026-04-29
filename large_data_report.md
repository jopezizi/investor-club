# Suuren tietomäärän testaaminen & käsittely


Käytetty seuraavanlaista skriptiä testiaineiston luomiseen:
* 1000 käyttäjää
* 100 000 julkaisua
* 1 000 000 kommenttia

````
import random
import sqlite3
from werkzeug.security import generate_password_hash

db = sqlite3.connect("database.db")

db.execute("DELETE FROM recommendations")
db.execute("DELETE FROM user_likes")
db.execute("DELETE FROM comments")
db.execute("DELETE FROM posts")
db.execute("DELETE FROM categories")
db.execute("DELETE FROM users")

user_count = 1000
post_count = 10 ** 5
comment_count = 10 ** 6



markets = ["OMX Helsinki", "OMX Stockholm", "NYSE / NASDAQ", "DAX", "Kehittyvät markkinat", "Kryptomarkkinat"]


industries = ["Teknologia", "Rahoitus", "Terveydenhuolto", "Teollisuus", "Kulutustavarat", "Energia", "Kiinteistöt"]

strategies = ["Arvosijoittaminen", "Kasvusijoittaminen", "Osinkosijoittaminen", "Indeksisijoittaminen", "Laatusijoittaminen", "Käänneyhtiö", "Vastuullisuus"]

recommendations_list = ["Osta", "Pidä", "Myy"]

categories_data = [
    ("Markkinat", "OMX Helsinki"),
    ("Markkinat", "OMX Stockholm"),
    ("Markkinat", "NYSE / NASDAQ"),
    ("Markkinat", "DAX"),
    ("Markkinat", "Kehittyvät markkinat"),
    ("Markkinat", "Kryptomarkkinat"),
    ("Toimialat", "Teknologia"),
    ("Toimialat", "Rahoitus"),
    ("Toimialat", "Terveydenhuolto"),
    ("Toimialat", "Teollisuus"),
    ("Toimialat", "Kulutustavarat"),
    ("Toimialat", "Energia"),
    ("Toimialat", "Kiinteistöt"),
]


for i in range(1, user_count + 1):
    password_hash = generate_password_hash("password123")
    db.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, datetime('now', 'localtime'))",
               [f"user{i}", password_hash])

for class_name, category_name in categories_data:
    db.execute("INSERT INTO categories (class, name) VALUES (?, ?)",
               [class_name, category_name])

for i in range(1, post_count + 1):
    user_id = random.randint(1, user_count)
    market = random.choice(markets)
    industry = random.choice(industries)
    strategy = random.choice(strategies)
    recommendation = random.choice(recommendations_list)
    
    db.execute("""INSERT INTO posts (title, content, market, industry, strategy, sent_at, user_id, recommendation)
                  VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'), ?, ?)""",
               [f"Post {i} - {market}", f"Test post number {i}. Market: {market}, Industry: {industry}, Strategy: {strategy}", 
                market, industry, strategy, user_id, recommendation])

for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    post_id = random.randint(1, post_count)
    
    db.execute("""INSERT INTO comments (content, sent_at, user_id, post_id)
                  VALUES (?, datetime('now', 'localtime'), ?, ?)""",
               [f"Test data", user_id, post_id])

for post_id in range(1, min(post_count + 1, 200)):
    for _ in range(random.randint(1, 5)):
        user_id = random.randint(1, user_count)
        recommendation = random.choice(recommendations_list)
        
        try:
            db.execute("INSERT INTO recommendations (user_id, post_id, recommendation) VALUES (?, ?, ?)",
                       [user_id, post_id, recommendation])
        except sqlite3.IntegrityError:
            pass

db.commit()
db.close()

````

Havaitaan, että sivulla kestää huomattavasti kauemmin ladata. 
Laaditaan sivutus.

Muutetaan ```app.py``` seuraavanlaisesti:

````
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
````

Muutetaan ```posts.py``` seuraavanlaisesti. Haetaan yhden sivun verran julkaisuja kerrallaan.

````
def get_posts(page, page_size) -> list:
    sql = '''SELECT
                p.id, p.title, strftime('%d.%m.%Y %H:%M', p.sent_at) AS sent_at, p.user_id, u.username, p.likes, p.buys, p.sells, p.market,
                p.industry, p.strategy, p.recommendation, p.image
            FROM posts p
            JOIN users u ON P.user_id = u.id
            ORDER BY p.id DESC
            LIMIT ? OFFSET ?
            '''
    limit = page_size
    offset = page_size * (page -1)
    return db.query(sql, [limit, offset])
````

Ja lisätään sivunavigointi ```index.html```:

````
  <p class="page_nav">
    <a href="/{{ page - 1 }}">&lt;&lt;</a>
    Sivu {{ page }}/{{ page_count }}
    <a href="/{{ page + 1 }}">&gt;&gt;</a>
  </p>
  <hr />
````
