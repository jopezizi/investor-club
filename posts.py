import db

def get_posts():
    sql = '''SELECT p.id, p.title, p.sent_at, p.user_id, u.username, p.likes, p.buys, p.sells
            FROM posts p
            JOIN users u ON P.user_id = u.id
            ORDER BY p.id DESC
            '''
    rows = db.query(sql)
    return [{"id": row["id"], "title": row["title"], "sent_at": row["sent_at"], "user_id": row["user_id"], "username": row["username"], "likes": row["likes"], "buys": row["buys"], "sells": row["sells"]} for row in rows]


def add_post(title, content, user_id):
    sql = '''
        INSERT INTO posts (title, content, sent_at, user_id) VALUES(?, ?, datetime('now', 'localtime'), ?)
        '''
    db.execute(sql, [title, content, user_id])
    return db.last_insert_id()
    
def get_post(post_id):
    sql = '''SELECT p.id, p.title, p.content, p.sent_at, p.user_id, u.username, p.likes, p.buys, p.sells
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
            '''
    rows = db.query(sql, [post_id])
    if rows:
        row = rows[0]
        return [{'id': row['id'], 'title': row['title'], 'content': row['content'], 'sent_at': row['sent_at'], 'user_id': row['user_id'], 'username': row['username'], 'likes': row['likes'], 'buys': row['buys'], 'sells': row['sells']}]
    else:
        return 'Post not found'

def get_comments(post_id):
    sql = '''SELECT c.id, c.content, c.sent_at, c.user_id, c.post_id
            FROM comments c
            WHERE c.post_id = ?
        '''
    rows = db.query(sql, [post_id])
    if rows:
        return [{'id': row['id'], 'content': row['content'], 'sent_at': row['sent_at'], 'user_id': row['user_id'], 'post_id': row['post_id']} for row in rows]
    else:
        return 'No comments'
    

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