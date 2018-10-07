import pymysql
import re
#闯进数据库链接对象
db=pymysql.connect(host='localhost',user='root',passwd='123456',
    db='dicts')
cur=db.cursor()

f=open('dict.txt')
pattern=r"\s+"
for x in f:
    data=re.split(pattern,x)
    if not data:
        break
    word=data[0]
    explains=" ".join(data[1:])
    sql="insert into words(word,explains) values('%s','%s')"%\
    (word,explains)
    try:
        cur.execute(sql)
        db.commit()
    except:
        db.rollback()

f.close()
cur.close()
db.close()

