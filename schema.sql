CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               username TEXT UNIQUE,
               password_hash TEXT,
                created_at TEXT,
                image BLOB
);
CREATE TABLE IF NOT EXISTS posts (
               id INTEGER PRIMARY KEY,
               title TEXT,
               content TEXT,
               market TEXT,
               industry TEXT,
               strategy TEXT,
               sent_at TEXT,
               user_id INTEGER REFERENCES users,
               likes INTEGER,
               buys INTEGER,
               sells INTEGER
);
CREATE TABLE IF NOT EXISTS comments (
               id INTEGER PRIMARY KEY,
               content TEXT,
               sent_at TEXT,
               user_id INTEGER REFERENCES users,
               post_id INTEGER REFERENCES posts
);