from peewee import SqliteDatabase

db = SqliteDatabase('level1.db')

db.execute_sql('''
    DROP TABLE IF EXISTS user
''')
db.execute_sql('''
    DROP TABLE IF EXISTS sessions
''')
db.execute_sql('''
    DROP TABLE IF EXISTS blogs
''')
db.execute_sql('''
    DROP TABLE IF EXISTS comments
''')

db.execute_sql('''
    CREATE TABLE user (username TEXT PRIMARY KEY, phash TEXT NOT NULL)
''')

db.execute_sql('''
    CREATE TABLE sessions (username TEXT PRIMARY KEY, sessionKey TEXT NOT NULL, FOREIGN KEY(username) REFERENCES user(username))
''')

db.execute_sql('''
    CREATE TABLE blogs (id INTEGER PRIMARY KEY, author TEXT NOT NULL, title TEXT NOT NULL, privacy INTERGER NOT NULL, content TEXT, FOREIGN KEY(author) REFERENCES user(username))
''')

db.execute_sql('''
    CREATE TABLE comments (id INTEGER PRIMARY KEY, author TEXT NOT NULL, post INTEGER NOT NULL,
    FOREIGN KEY(author) REFERENCES user(username),
    FOREIGN KEY(post) REFERENCES blogs(id))
''')