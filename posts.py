import app
import sqlite3

def get_posts():
    sql = '''SELECT p.id, p.title, p.sent_at, p.user_id, u.username
            FROM posts p
            JOIN users u ON P.user_id = u.id
            ORDER BY p.id DESC
            '''
    rows = app.query(sql)
    return [{"id": row[0], "title": row[1], "sent_at":row[2], "user_id": row[3],"username": row[4]} for row in rows]


def add_post(title, content, user_id):
    sql = '''
        INSERT INTO posts (title, content, sent_at, user_id) VALUES(?, ?, datetime('now', 'localtime'), ?)
        '''
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(sql, (title, content, user_id))
        return cursor.lastrowid
    
def get_post(post_id):
    sql = '''SELECT p.id, p.title, p.content, p.sent_at, p.user_id, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
            '''
    post = app.query(sql,(post_id))
    if post:
        return [{'id':post[0][0], 'title':post[0][1],'content':post[0][2],'sent_at':post[0][3],'user_id':post[0][4], 'username':post[0][5]}]
    else:
        return 'Post not found'

def get_comments(post_id):
    sql = '''SELECT c.id, c.content, c.sent_at, c.user_id, c.post_id
            FROM comments c
            WHERE c.post_id = ?
        '''
    comments = app.query(sql, (post_id))
    if comments:
        return [{'id':comments[0][0], 'content':comments[0][1],'sent_at':comments[0][2],'user_id':comments[0][3],'post_id':comments[0][4]}]
    else:
        return 'No comments'
    

def search(query):
    sql = '''SELECT p.id, p.title, p.content, p.sent_at, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.content LIKE ?
            ORDER BY p.sent_at DESC
            '''
    return app.query(sql, ('%' + query + '%'))