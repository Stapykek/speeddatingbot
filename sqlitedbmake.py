import sqlite3
sql = sqlite3.connect('forum.db')
cur = sql.cursor()
com = " select * from participants where tg = 'stapykek' "
cur = sql.execute(com)
arr = cur.fetchall()
