'''
author:lvpeng
email:1310450611@qq.com
description:look through  words
date:2018-10-01
'''
import gevent
from gevent import monkey
monkey.patch_all()
from socket import *
import re
import signal
import time
import  sys
import pymysql


DICT_PATH='./dict.txt'

class TcpServer(object):
    '''类封装所有代码'''
    def __init__(self,addr,db,query_db,hist_db):
        self.s=socket()
        self.s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.ADDR=addr
        self.host=addr[0]
        self.port=addr[1]
        self.db=db
        self.query_db=query_db
        self.hist_db=hist_db
        self.bind()

    def bind(self):
        self.s.bind(self.ADDR)
        self.s.listen(10)

    def sever_gevent(self):
        while True:
            try:
                c,addr=self.s.accept()
            except KeyboardInterrupt:
                sys.exit("服务端退出")
            except Exception as e:
                print(e)
                sys.exit(0)

            print("connect from :",c.getpeername())
            
            gevent.spawn(self.handler,c)


    # 协程事件对象
    def handler(self,c):
        while True:
            msg=c.recv(4096).decode()
            data=msg.split()
            # print(data[0])
            if data[0]=="R":
                self.do_register(c,data)
            elif data[0]=="L":
                self.do_login(c,data)
            elif data[0]=="Q":
                # print("执行查询操作")
                self.do_query(c,data)
            elif data[0]=="H":
                self.do_hist(c,data)
            elif data[0]=="E":
                print("客户端退出",c)
                c.close()
                break


    def  do_register(self,c,data):
        ''' 服务端处理注册 '''
        
        user=data[1]
        passwd=data[2]
        sql="select name,passwd from user where name='%s' \
        and passwd='%s';"%(user,passwd)

        cur=self.db.cursor()
        cur.execute(sql)
        print("fetch one:",cur.fetchone())
        #如果该用户已经存在
        if cur.fetchone():
            c.send(b"Fail")
            cur.close()
            return  

        c.send(b'Ok')
        # print(user,passwd)
        add_user_sql="insert into user(name,passwd) values('%s',\
        '%s')"%(user,passwd)
        try:
            cur.execute(add_user_sql)
            self.db.commit()
        except:
            self.db.rollback()
        cur.close()
        print("%s注册成功"%user)

    def do_login(self,c,data):
        ''' 服务端处理登录事件'''
        user=data[1]
        pwd=data[2]
        cur=self.db.cursor()
        sql="select  name,passwd from user where name='%s' \
        and passwd='%s';"%(user,pwd)

        cur.execute(sql)

        user_msg=cur.fetchone()
        cur.close()
        if user_msg:
            #有该用户信息，，让其成功登录
            c.send(b'Ok')
            print("登录成功")
        else:
            c.send(b'Fail')
            print("登陆失败")
            return 
    def do_query(self,c,data):
        '''服务端处理查询操作'''
        user=data[1]
        word=data[2]
        query_sql="select explains from words where word='%s'"%word
        cur=self.query_db.cursor()
        cur.execute(query_sql)
        explain=cur.fetchone()
        if explain:
            c.send(b"Ok")
            time.sleep(0.1)
            c.send(explain[0].encode())
            self.do_insert_hist(user,word)
        else:
            c.send(b"Fail")
        cur.close()
    #将查询记录插入数据库
    def do_insert_hist(self,user,word):
        ''' 首先创建查询记录数据库数据库：
        hists---->表hist -->
        字段id  user word time'''
        cur=self.hist_db.cursor()
        insert_hist_sql="insert into hist(user,word) values('%s','%s');\
        "%(user,word)
        try:
            cur.execute(insert_hist_sql)
            self.hist_db.commit()
        except:
            self.hist_db.rollback()
        cur.close()
#     查询记录结果查询
    def do_hist(self,c,data):
        print("记录查询操作")
        user=data[1]
        hist_sql="select id,word,time from hist where user='%s';"%(user)
        cur=self.hist_db.cursor()

        cur.execute(hist_sql)
        hists=cur.fetchall()
        if hists:
            c.send(b"Ok")
            for x  in hists:
                hist_str=[str(y) for y in x ]
                time.sleep(0.1)
                c.send(" ".join(hist_str).encode())
                time.sleep(0.1)
            c.send("##".encode())
        else:
            c.send(b"Fail")
        cur.close()

if __name__=="__main__":
    HOST='0.0.0.0'
    PORT=9999
    ADDR=(HOST,PORT)
    '''创建数据库连接对象 '''
    db=pymysql.connect(host="0.0.0.0",user="root",passwd="123456",
        db="users")
    query_db=pymysql.connect(host="0.0.0.0",user="root",passwd="123456",
        db="dicts")
    hist_db=pymysql.connect(host="0.0.0.0",user="root",passwd="123456",
        db="hists")
    tcpServer=TcpServer(ADDR,db,query_db,hist_db)
    tcpServer.sever_gevent()