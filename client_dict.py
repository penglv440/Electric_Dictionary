'''
client
'''
from socket import *
import sys,time,getpass

class ClientServer(object):
    '''客户端类封装'''
    def __init__(self,addr):
        self.s=socket()
        self.ADDR=addr
        self.HOST=addr[0]
        self.PORT=addr[1]

    def serve_forever(self):
        self.s.connect(self.ADDR)
        print("connected with server---")

        #启动一级界面
        self.show_first_menu()

    def show_first_menu(self):
        while True:
            print("=======选项==========")
            print("=======1.注册========")
            print("=======2.登录========")
            print("=======3.退出========")
            try:
                chose1=int(input("请输入选项:"))
            except Exception as e:
                print(e)
                print("请重新输入")
                continue

            if chose1==1:
                self.do_register()

            elif chose1==2:
                self.do_login()

            elif chose1==3:
                self.s.send(b"E")
                sys.exit("客户端退出")

    def do_register(self):
        ''' 用户注册处理函数'''
        print("注册操作")
        while True:
            user=input("请输入用户名")
            passwd=getpass.getpass("请输入密码:")
            passwd_check=getpass.getpass("确认密码:")
            if passwd==passwd_check:
                if (' ' in user) or (' ' in passwd):
                    print("用户名或密码不能存在空格")
                    continue
                register_msg="R {} {}".format(user,passwd)
                self.s.send(register_msg.encode())
                data=self.s.recv(4096).decode()
                if data=="Ok":
                    print("注册成功")
                    #注册成功，直接跳转到登录界面
                    self.do_login()
                    return
                elif data=="Fail":
                    print("用户已存在")
                    continue
            else:
                print("您两次输入的密码不一致，请您重新输入")
                continue

    def do_login(self):
        '''用户登录处理函数'''
        print("登录操作")
        while True:
            user=input("用户名:")
            passwd=getpass.getpass("密码")
            if (' ' in user) or (' ' in passwd):
                print("您输入的用户名或密码存在空格")
                continue
            login_msg="L {} {}".format(user,passwd)

            self.s.send(login_msg.encode())
            # 接收服务端回馈消息
            data=self.s.recv(4096).decode()
            if data=="Ok":
                print("登录成功")
                #进入二级查询界面
                self.query_words(user)
                return
            elif data=="Fail":
                print("您的输入有误，请您重新输入")

                continue
    def query_words(self,user):
        ''' 用户查询单词操作'''
        while True:
            print("+++++++++++++++查询选项+++++++++++++++")
            print("+++++++++++++++1.单词查询+++++++++++++")
            print("+++++++++++++++2.纪录查询+++++++++++++")
            print("+++++++++++++++3.退回到一级界面++++++++")
            try:
                query_chose=int(input("请输入选项："))
            except Exception as e:
                print(e)
                continue
            if query_chose==1:
                #单词查询选项
                self.do_query_word(user)
            elif query_chose==2:
                #历史纪录查询选项
                self.do_query_hist(user)
            elif query_chose==3:
                return 

    def do_query_word(self,user):
        '''单词查询选项'''
        print("您已进入查询单词选项")
        while True:
            word=input("请输入您想要查询的单词(##退出)：")
            if word=="##":
                break
            word_msg="Q {} {}".format(user,word)

            self.s.send(word_msg.encode())  

            data=self.s.recv(4096).decode()
            print("查询测试")
            if data=="Ok":
                explain=self.s.recv(4096).decode()
                print("解释:",explain)
            elif data=="Fail":
                print("您要查询的单词不存在")
        
    def do_query_hist(self,user):
        ''' 历史纪录查询选项'''
        print("您已进入记录查询选项")
        query_hist_msg="H {}".format(user)
        self.s.send(query_hist_msg.encode())
        data=self.s.recv(4096).decode()
        if data=="Ok":
            while True:
                query_hist=self.s.recv(4096).decode()
                if query_hist=="##":
                    break
                print(query_hist)
        elif data=="Fail":
            print("您要查找的历史记录为空")

if __name__=="__main__":
    '''主事件循环'''
    if len(sys.argv)<3:
        sys.exit("您输入的参数有误")
    HOST=sys.argv[1]
    PORT=int(sys.argv[2])
    ADDR=(HOST,PORT)
    clientServer=ClientServer(ADDR)
    clientServer.serve_forever()