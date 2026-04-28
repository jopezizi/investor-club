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
               likes INTEGER NOT NULL DEFAULT 0,
               buys INTEGER NOT NULL DEFAULT 0,
               sells INTEGER NOT NULL DEFAULT 0,
               holds INTEGER NOT NULL DEFAULT 0,
               recommendation TEXT,
               image BLOB
);

CREATE TABLE IF NOT EXISTS comments (
               id INTEGER PRIMARY KEY,
               content TEXT,
               sent_at TEXT,
               user_id INTEGER REFERENCES users,
               post_id INTEGER REFERENCES posts
);

CREATE TABLE IF NOT EXISTS user_likes (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    recommendation TEXT NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    class TEXT NOT NULL,
    name TEXT NOT NULL
);
