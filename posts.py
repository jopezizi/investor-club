import app

def get_posts():
    sql = '''SELECT a.id, a.title, a.user_id
            FROM analysis a
            ORDER BY a.id DESC
            '''
    rows = app.query(sql)
    return [{"id": row[0], "title": row[1], "user_id": row[2]} for row in rows]