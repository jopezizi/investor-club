import db

def get_posts():
    sql = '''SELECT p.id, p.title, strftime('%d.%m.%Y %H:%M', p.sent_at) AS sent_at, p.user_id, u.username, p.likes, p.buys, p.sells, p.market, p.industry, p.strategy, p.recommendation
            FROM posts p
            JOIN users u ON P.user_id = u.id
            ORDER BY p.id DESC
            '''
    return db.query(sql)


def add_post(title, content, user_id, market, industry, strategy, recommendation):
    sql = '''
        INSERT INTO posts (title, content, sent_at, user_id, market, industry, strategy, recommendation) VALUES(?, ?, datetime('now', 'localtime'), ?, ?, ?, ?, ?)
        '''
    db.execute(sql, [title, content, user_id, market, industry, strategy, recommendation])
    return db.last_insert_id()
    
def get_post(post_id):
    sql = '''SELECT p.id, p.title, p.content, strftime('%d.%m.%Y %H:%M', p.sent_at) AS sent_at, p.user_id, u.username, p.likes, p.buys, p.sells, p.market, p.industry, p.strategy, p.recommendation, p.holds
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
            '''
    result = db.query(sql, [post_id])
    return result[0] if result else None

def search(query):
    sql = '''SELECT p.id, p.title, p.content, p.sent_at, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.content LIKE ?
            OR p.title LIKE ?
            ORDER BY p.sent_at DESC
            '''
    return db.query(sql, ['%' + query + '%', '%' + query + '%'])

def update_post(post_id, title, content):
    sql = "UPDATE posts SET title = ?, content = ? WHERE id = ?"
    db.execute(sql, [title, content, post_id])

def remove_post(post_id):
    sql = "DELETE FROM posts WHERE id = ?"
    db.execute(sql, [post_id])

def get_user_liked(user_id, post_id):
    sql = 'SELECT 1 FROM user_likes WHERE user_id = ? AND post_id = ?'
    return db.query(sql, [user_id, post_id])

def add_like(user_id, post_id):
    sql = 'INSERT INTO user_likes (user_id, post_id) VALUES (?,?)'
    db.execute(sql, [user_id, post_id])
    sql = 'UPDATE posts SET likes = likes + 1 WHERE id = ?'
    db.execute(sql, [post_id] )

def delete_like(user_id, post_id):
    sql = 'DELETE FROM user_likes WHERE user_id = ? AND post_id = ?'
    db.execute(sql, [user_id, post_id])
    sql = 'UPDATE posts SET likes = likes - 1 WHERE id = ? AND likes > 0'
    db.execute(sql, [post_id] )

def get_user_recommended(user_id, post_id):
    sql = 'SELECT recommendation FROM recommendations WHERE user_id = ? AND post_id = ?'
    return db.query(sql, [user_id, post_id])

def update_recommendation(user_id, post_id, recommended, recommendation):
    old_recommendation = recommended[0]['recommendation'] if recommended else None

    if recommendation == old_recommendation:
        return

    buy = 0
    hold = 0
    sell = 0

    if old_recommendation == 'buy':
        buy -= 1
    elif old_recommendation == 'sell':
        sell -= 1
    elif old_recommendation == 'hold':
        hold -= 1

    if recommendation == 'clear':
        if old_recommendation is not None:
            sql = 'DELETE FROM recommendations WHERE user_id = ? AND post_id = ?'
            db.execute(sql, [user_id, post_id])
        sql = 'UPDATE posts SET buys = buys + ?, holds = holds + ?, sells = sells + ? WHERE id = ?'
        db.execute(sql, [buy, hold, sell, post_id])
        return
    
    if old_recommendation is None:
        sql = 'INSERT INTO recommendations (user_id, post_id, recommendation) VALUES (?, ?, ?)'
        db.execute(sql, [user_id, post_id, recommendation])
    else:
        sql = 'UPDATE recommendations SET recommendation = ? WHERE user_id = ? AND post_id = ?'
        db.execute(sql, [recommendation, user_id, post_id])



    
    if recommendation == 'buy':
        buy += 1
    elif recommendation == 'sell':
        sell +=1
    elif recommendation == 'hold':
        hold += 1

    sql = 'UPDATE posts SET buys = buys + ?, holds = holds + ?, sells = sells + ? WHERE id = ?'
    db.execute(sql, [buy, hold, sell, post_id])


def get_classes():
    sql = 'SELECT DISTINCT class FROM categories ORDER BY class'
    result = db.query(sql)
    return result if result else None

def get_category_items(category):
    sql = 'SELECT class, name, id FROM categories WHERE class = ? ORDER BY name'
    return db.query(sql, [category])

def get_category_info(id):
    sql = 'SELECT class, name FROM categories WHERE id = ?'
    return db.query(sql, [id])


def get_posts_by_category(cat_class, category):
    if cat_class == 'Markkina':
        where = 'p.market = ?'
    elif cat_class == 'Toimiala':
        where = 'p.industry = ?'
    elif cat_class == 'Strategia':
        where = 'p.strategy = ?'
    else:
        return []

    sql = f'''SELECT p.id, p.title, strftime('%d.%m.%Y %H:%M', p.sent_at) AS sent_at, p.user_id, u.username, p.likes, p.buys, p.sells, p.market, p.industry, p.strategy, p.recommendation
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE {where}
            ORDER BY p.likes DESC
            '''
    return db.query(sql, [category])

def get_comments(post_id):
    sql = '''SELECT c.id, c.content, strftime('%d.%m.%Y %H:%M', c.sent_at) AS sent_at, c.user_id, u.username FROM comments c, users u WHERE c.user_id = u.id AND c.post_id = ? ORDER BY c.id'''
    return db.query(sql, [post_id])

def add_comment(content, user_id, post_id):
    sql = '''INSERT INTO comments (content, sent_at, user_id, post_id) VALUES (?, datetime('now'), ?,?)'''
    db.execute(sql, [content, user_id, post_id])

def get_recommendation_distribution(user_id):
    sql = '''SELECT 
                SUM(CASE WHEN recommendation = 'Osta' THEN 1 ELSE 0 END) AS buys,
                SUM(CASE WHEN recommendation = 'Myy' THEN 1 ELSE 0 END) AS sells,
                SUM(CASE WHEN recommendation = 'Pidä' THEN 1 ELSE 0 END) AS holds
            FROM posts WHERE user_id = ?;'''
    return db.query(sql, [user_id])

def get_user_total_likes(user_id):
    sql = '''SELECT SUM(likes) as likes FROM posts WHERE user_id = ?'''
    return db.query(sql, [user_id])