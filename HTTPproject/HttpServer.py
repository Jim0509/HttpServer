# HttpServer.py
# 多线程HttpServer网络服务器
from socket import *
import sys
from threading import Thread
import re, time
from settings import *

# WebFrame通信函数
# 返回客户端要请求的文件内容
def connect_frame(METHOD, PATH_INFO):
    s = socket() # 创建socket
    try:
        s.connect(frame_address)#连接其它服务器
    except:
        print("Connect err")
        return
    s.send(METHOD.encode()) #发送请求方法 GET
    time.sleep(0.1)
    s.send(PATH_INFO.encode())#发送请求文件路径
    resp = s.recv(4096).decode()#接收结果
    if not resp:
        s.close()
        return "404"
    else:
        s.close()
        return resp  #返回文件内容

# 封装HttpServer类
class HTTPServer(object):
    def __init__(self, address):
        self.address = address
        self.create_socket()#创建socket
        self.bind(address) #绑定

    # 创建套接字
    def create_socket(self):
        self.sockfd = socket() 
        self.sockfd.setsockopt(
            SOL_SOCKET, SO_REUSEADDR, 1
        )

    # 绑定
    def bind(self, address):
        self.ip = address[0] #ip
        self.port = address[1]#端口
        self.sockfd.bind(address)#绑定

    # 启动服务器
    def server_foever(self):
        self.sockfd.listen(10)
        print("Server start on ", self.port) 
        while True:
            connfd,addr = self.sockfd.accept() 
            print("Connect from ", addr)

            handle_client = Thread(
                target=self.handle, 
                args=(connfd,))#创建处理线程
            handle_client.setDaemon(True)
            handle_client.start() #启动线程

    # 定义具体处理客户端请求函数
    def handle(self, connfd):
        # 接收来自客户端的请求数据
        request = connfd.recv(4096)
        if not request:  # 没读到数据
            connfd.close() #关闭socket
            return

        # 将请求数据按换行符进行拆分    
        request_lines = request.splitlines()
        # 获取请求行
        request_line = request_lines[0].decode("utf-8")
        print(request_line)
        # 判断请求行的合法性
        pattern = r'(?P<METHOD>[A-Z]+)\s+(?P<PATH_INFO>/\S*)'  
        try:
            p =re.match(pattern,request_line) 
            env = p.groupdict()#返回匹配到的所有命名子组的字典
            print(env)
        except: # 请求行异常,直接返回错误 
            response = "HTTP/1.1 500 SERVER ERROR\r\n"
            response += "\r\n" # 空行,包头和包体分隔符
            response += "Server error"
            connfd.send(response.encode())#发送响应
            connfd.close() #关闭通信socket
            return
        # 正常数据处理  GET /index.html HTTP/1.1
        content = connect_frame(**env)#调用另外的服务处理
        response = ""
        if content == "404": #文件未找到
            header = "HTTP/1.1 404 Not Found\r\n"
            header += "\r\n"
            body = "Sorry, not found the page"
            response = header + body
        else: #文件找到,正常返回
            header = "HTTP/1.1 200 OK\r\n"
            header += "\r\n"
            #将文件内容作为body部分
            response = header + content 
        connfd.send(response.encode())
        connfd.close()

if __name__ == "__main__":
    httpserver = HTTPServer(ADDR)
    httpserver.server_foever() #启动服务器