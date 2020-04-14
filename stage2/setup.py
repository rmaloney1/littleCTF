from peewee import SqliteDatabase
from hashlib import md5

db = SqliteDatabase('level2.db')


# flags:
# flag0 XSS on search
# flag1 SSTI on search
# flag2 adminPassword
# flag3 yaml vulnerability

flags = ['SLKDGJ', 'PXTWAS', 'carlos420', 'YGTHSW']
other_users = ['davo', 'admin0', 'denice']

if __name__ == "__main__":

    db.execute_sql('''
        INSERT INTO user (username, phash) VALUES ('admin0', ?)
    ''', (md5(flags[2].encode('utf-8')).hexdigest(),))

    db.execute_sql('''
        INSERT INTO user (username, phash) VALUES ('davo', 'flag2 is FLAG_2_ + admin0 password')
    ''')

    db.execute_sql('''
        INSERT INTO user (username, phash) VALUES ('denice', 'this is md5, super secure! no salt required')
    ''')

    flightsList = [["QA587", "Qantas", "PER", "SYD", "14-04-2020 02:41", "14-04-2020 06:53"],
                    ["VA846", "Virgin Australia", "ADL", "MEL", "20-04-2020 15:34", "20-04-2020 16:57"],
                    ["JQ989", "Jetstar", "SYD", "BNE", "10-04-2020 12:41", "10-04-2020 11:53"],
                    ["QA691", "Qantas", "HBA", "MEL", "14-04-2020 23:41", "15-04-2020 00:10"]
    ]
    for flight in flightsList:
        db.execute_sql('''
            INSERT INTO flights (code, airline, departsFrom, goingTo, departTime, arriveTime)
            VALUES (?, ?, ?, ?, ?, ?)
        ''',(flight[0], flight[1], flight[2], flight[3], flight[4], flight[5]))