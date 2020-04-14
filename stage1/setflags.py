from peewee import SqliteDatabase

db = SqliteDatabase('level1.db')


# flags:
# flag0 private blog from some user - path inj
# flag1 editing another's blog - non ath
# flag2 logging on as another user -sqli
# flag3 obtaining pword hash of another user -sqli
# flag4 stored xss - stored xss

flags = ['HDOQTY', 'PDJVLW', 'MDOPKG', 'QSPMEP', 'QNZKPQ']
other_users = ['richard', 'admin', 'Joe']

if __name__ == "__main__":
    db.execute_sql('''
        INSERT INTO blogs (author, title, privacy, content) VALUES ('richard', 'Super Secret Stuff', 1, ?)
    ''',("FLAG_0_" + flags[0],))

    db.execute_sql('''
        INSERT INTO blogs (author, title, privacy, content) VALUES ('Joe', 'No swearing', 0, '<h1>I will personally report anyone who swears in a blog!</h1>')
    ''')
    db.execute_sql('''
        INSERT INTO blogs (author, title, privacy, content) VALUES ('Joe', 'Don''t Read This', 0, 'Oh no!!')
    ''')
    db.execute_sql('''
        INSERT INTO blogs (author, title, privacy, content) VALUES ('admin', 'Helloe', 0, 'Welcome to Zoom Blogs! We are super secure, scripts will not run in blog posts so no XSS!')
    ''')

    db.execute_sql('''
        INSERT INTO user (username, phash) VALUES ('admin', ?)
    ''', ("FLAG_3_" + flags[3],))

    db.execute_sql('''
        INSERT INTO user (username, phash) VALUES ('richard', 'noRichardDoesntHaveTheFlag')
    ''')

    db.execute_sql('''
        INSERT INTO user (username, phash) VALUES ('Joe', 'thisisarandomhash')
    ''')

    db.execute_sql('''
        INSERT INTO sessions (username, sessionKey) VALUES ('Joe', 'FLAG_4_QNZKPQ')
    ''')
