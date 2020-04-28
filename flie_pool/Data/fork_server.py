"""
    基于fork的多进程网络并发
    重点代码
"""
import os
import sys
from socket import *
import signal


def handle(connfd):
    print("客户端地址：", connfd.getpeername())
    while True:
        data = connfd.recv(1024)
        if not data:
            break
        print(data.decode())
        connfd.send(b"OK")
    connfd.close()


# 服务器地址
HOST = "0.0.0.0"
PORT = 6712
ADDR = (HOST, PORT)

# 创建监听套接字
sockfd = socket(AF_INET, SOCK_STREAM)
sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sockfd.bind(ADDR)
sockfd.listen(4)

# 僵尸进程的处理
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

print("Listen the port 6712 ... ")

# 循环等待客户端连接
while True:
    try:
        connfd, addr = sockfd.accept()
    except KeyboardInterrupt:
        sys.exit("服务器退出")
    except Exception as e:
        print(e)
        continue
    # 创建子进程处理客户端请求
    pid = os.fork()
    if pid == 0:
        sockfd.close()  # 子进程不需要该套接字，只需要连接套接字
        handle(connfd)  # 具体处理客户端请求
        os._exit(0)
    # 父进程实际只用来处理客户端连接
    else:
        connfd.close()  # 父进程不需要连接套接字
