import db

def get_user(user_id):
    sql = '''SELECT u.id, u.username, strftime('%d.%m.%Y', u.created_at) AS created_at,
            timediff(datetime('now', 'localtime'), u.created_at) AS ago
            FROM users u
            WHERE u.id = ?
            '''
    rows = db.query(sql, [user_id])
    if rows:
        row = rows[0]
        return [{'id': row['id'], 'username': row['username'], 'created_at': row['created_at'], 'ago': row['ago']}]
    else:
        return 'User not found'

def get_posts(user_id):
    sql = '''SELECT p.id, p.title, p.content, strftime('%d.%m.%Y %H:%M', p.sent_at) AS sent_at, p.likes, p.buys, p.sells
            FROM posts p
            WHERE p.user_id = ?
            ORDER BY p.sent_at DESC
            '''
    return db.query(sql, [user_id])