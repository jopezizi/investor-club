import db
import sqlite3

def authenticate_user(username, password_hash):
    sql = "SELECT password_hash, id FROM users WHERE username = ?"
    user_info = db.query(sql, [username])
    return user_info[0] if user_info else None

def create_user(username, password_hash):
    try:
        sql = "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, datetime('now', 'localtime'))"
        db.execute(sql, [username, password_hash])
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(user_id):
    sql = '''SELECT u.id, u.username, strftime('%d.%m.%Y', u.created_at) AS created_at,
            CAST((JULIANDAY('now') - JULIANDAY(u.created_at)) AS INTEGER) AS ago, u.image IS NOT NULL has_image
            FROM users u
            WHERE u.id = ?
            '''
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_posts(user_id):
    sql = '''SELECT p.id, p.title, p.content, strftime('%d.%m.%Y %H:%M', p.sent_at) AS sent_at, p.likes, p.buys, p.sells
            FROM posts p
            WHERE p.user_id = ?
            ORDER BY p.sent_at DESC
            '''
    return db.query(sql, [user_id])

def get_profile_picture(user_id):
    sql = '''SELECT u.image
            FROM users u
            WHERE u.id = ?
            '''
    result = db.query(sql, [user_id])
    return result[0] if result else None

def update_profile_picture(user_id, image):
    sql = 'UPDATE users SET image = ? WHERE id = ?'
    db.execute(sql, [image, user_id])

def delete_profile_picture(user_id):
    sql = 'UPDATE users SET image = NULL WHERE id = ?'
    db.execute(sql, [user_id])
