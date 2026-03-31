import app, posts, sqlite3

def get_user(user_id):
    sql = '''SELECT u.id, u.username
            FROM users u
            WHERE u.id = ?
            '''
    profile = app.query(sql,(user_id))
    if profile:
        return [{'id':profile[0][0], 'username':profile[0][1]}]
    else:
        return 'User not found'
