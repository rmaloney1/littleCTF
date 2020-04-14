from peewee import SqliteDatabase

db = SqliteDatabase('level2.db')

db.execute_sql('''
    DROP TABLE IF EXISTS user
''')
db.execute_sql('''
    DROP TABLE IF EXISTS sessions
''')
db.execute_sql('''
    DROP TABLE IF EXISTS flights
''')

db.execute_sql('''
    CREATE TABLE user (username TEXT PRIMARY KEY, phash TEXT NOT NULL)
''')

db.execute_sql('''
    CREATE TABLE sessions (username TEXT PRIMARY KEY, sessionKey TEXT NOT NULL, FOREIGN KEY(username) REFERENCES user(username))
''')

db.execute_sql('''
    CREATE TABLE flights (code TEXT PRIMARY KEY, airline TEXT NOT NULL, departsFrom TEXT NOT NULL, goingTo TEXT NOT NULL, departTime DATE NOT NULL, arriveTime DATE NOT NULL)
''')