"""
    基于多进程网络并发的TCP网络通信
    重点代码
"""
from multiprocessing import Process
from socket import *
import sys
import signal


def handle(connfd):
    print("client address:", connfd.getpeername())
    while True:
        data = connfd.recv(1024)
        if not data:
            connfd.close()
            return
        print(data.decode())
        connfd.send(b"OK")


def kill_zoobie():
    # 僵尸进程的处理
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)


def main():
    kill_zoobie()
    # 创建TCP套接字
    HOST = "0.0.0.0"
    PORT = 6712
    ADDR = (HOST, PORT)
    # 创建TCP套接字
    sockfd = socket(AF_INET, SOCK_STREAM)
    sockfd.bind(ADDR)
    sockfd.listen(4)
    # 循环处理客户端请求
    while True:
        try:
            connfd, addr = sockfd.accept()
        except KeyboardInterrupt:
            sys.exit("服务器关闭")
        except Exception as e:
            print(e)
        # 创建子进程处理客户端请求
        child_process = Process(target=handle, args=(connfd,))
        child_process.daemon = True
        child_process.start()


if __name__ == '__main__':
    main()
