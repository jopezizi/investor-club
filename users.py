import db

def get_user(user_id):
    sql = '''SELECT u.id, u.username, strftime('%d.%m.%Y', u.created_at) AS created_at,
            timediff(datetime('now', 'localtime'), u.created_at) AS ago
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