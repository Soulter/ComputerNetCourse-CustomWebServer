# coding = utf-8
import socket
import logging
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)

@dataclass
class Request():
    method: str
    url: str
    version: str
    header: dict
    body: bytes
    
class WebServer():
    '''
    Web 服务器类
    @author: U202141035 廖玮珑
    '''
    def __init__(self, port):
        self.port = port
        register_logger()
        self.route = {}
        
    def start(self):
        '''
        启动 Web 服务器
        '''
        # 创建套接字
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定套接字
        while True:
            try:
                tcp_server_socket.bind(("", self.port))
                logger.info("Web server is running on http://localhost:%d" % self.port)
                break
            except OSError as e:
                logger.warning("Port %d is already in use, try another one" % self.port)
                self.port += 1
        
        # 变为监听套接字
        tcp_server_socket.listen(128)
        while True:
            # 等待新客户端的连接
            new_socket, client_addr = tcp_server_socket.accept()
            # 为客户端提供服务
            # self.service_client(new_socket)
            # 我们暂时使用多线程提高并发性
            threading.Thread(target=self.service_client, args=(new_socket,)).start()
            
    def post(self, url):
        '''
        装饰器，用于注册路由
        '''
        def decorator(func):
            self.route[url] = {
                "method": "POST",
                "func": func
            }
            return func
        return decorator
    
    def get(self, url):
        '''
        装饰器，用于注册路由
        '''
        def decorator(func):
            self.route[url] = {
                "method": "GET",
                "func": func
            }
            return func
        return decorator
        
    def service_client(self, new_socket):
        # 接受浏览器的请求
        request = new_socket.recv(1024)
        # logger.info("Recv: %s" % request.decode("utf-8"))
        
        # 解析请求到 Request 对象
        request_obj = self.parse_request(request.decode("utf-8"))

        # 服务路由
        self.serve_route(request_obj, new_socket)
        
    
    def parse_request(self, request_str: str) -> Request:  
        '''
        解析请求字符串到 Request 对象
        '''
        request_lines = request_str.splitlines()
        request_line = request_lines[0]
        method, url, version = request_line.split()
        header = {}
        body = None
        for line in request_lines[1:]:
            if not line:
                continue
            key, value = line.split(": ")
            header[key] = value
        if method == "POST":
            body = request_lines[-1]
        request = Request(method, url, version, header, body)
        # logger.info("Request: %s" % request)
        return request

    
    def serve_route(self, request: Request, new_socket):
        '''
        根据路由表服务请求
        '''
        if request.url in self.route:
            if request.method == self.route[request.url]["method"]:
                ret = self.route[request.url]["func"](request)
                if not isinstance(ret, str):
                    self.response(new_socket, str(ret))
                else:
                    self.response(new_socket, ret)
                logger.info("200 OK - %s" % request.url)
            else:
                logger.warning("Method not allowed")
                self.response(new_socket, "Method not allowed")
        else:
            logger.warning("404 Not Found - %s" % request.url)
            self.response(new_socket, "404 Not Found")
            
    def response(self, new_socket, response):
        '''
        返回 HTTP 响应
        '''
        response = "HTTP/1.1 200 OK \r\n" + "\r\n" + response + "\r\n"
        new_socket.send(response.encode("utf-8"))
        new_socket.close()



def register_logger():
    global logger
    # 显示在屏幕上的日志
    console = logging.StreamHandler()
    # 设置日志打印格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    # 设置日志级别
    logger.setLevel(logging.DEBUG)
    # info级别设置整个颜色为绿色
    logging.addLevelName(logging.INFO, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
