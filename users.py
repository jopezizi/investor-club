import app, posts, sqlite3

def get_user(user_id):
    sql = '''SELECT u.id, u.username, strftime('%d.%m.%Y', u.created_at) AS created_at,
            timediff(datetime('now', 'localtime'), u.created_at) AS ago
            FROM users u
            WHERE u.id = ?
            '''
    profile = app.query(sql,(user_id))
    if profile:
        return [{'id':profile[0][0], 'username':profile[0][1], 'created_at':profile[0][2], 'ago':profile[0][3]}]
    else:
        return 'User not found'
