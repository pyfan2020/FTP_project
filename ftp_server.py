"""
    ftp文件传输服务端
    重点代码
"""
from socket import *
import sys
from threading import Thread
import os
import time

# 定义全局变量
HOST = "0.0.0.0"
PORT = 6712
ADDR = (HOST, PORT)
# 文件夹路径
FTP = "E:\Python学习文件\每日学习\第二阶段\concurrence\day04\FTP\\flie_pool\\"


# 将客户端请求功能封装为类
class FtpServer:
    def __init__(self, connfd, FTP_PATH):
        self.connfd = connfd
        self.FTP_PATH = FTP_PATH

    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.FTP_PATH)
        if not files:
            self.connfd.send("该文件类别为空。".encode())
            return
        else:
            self.connfd.send(b"OK")
        fs = ""
        for file in files:
            if files[0] != "." and os.path.isfile(self.FTP_PATH + file):
                fs += file + "\n"
        self.connfd.send(fs.encode())

    def do_get(self, file_name):
        try:
            fd = open(self.FTP_PATH + file_name, "rb")
        except IOError:
            self.connfd.send("文件不存在".encode())
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1)
        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(data)

    def do_put(self, file_name):
        files = os.listdir(self.FTP_PATH)
        if file_name in files:
            self.connfd.send(b"Error")
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1)
            fd = open(self.FTP_PATH + file_name, "wb")
            while True:
                data = self.connfd.recv(1024)
                if not data or data == b"##":
                    break
                fd.write(data)
            fd.close()


def handle(connfd):
    # 选择文件夹
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP + cls + '\\'
    ftp = FtpServer(connfd, FTP_PATH)
    while True:
        # 接收命令
        data = connfd.recv(1024).decode()
        # 若data为空或者为Q,则结束分支线程
        if not data or data[0] == "Q":
            return
        elif data[0] == "L":
            ftp.do_list()
        elif data[0] == "G":
            file_name = data.split(" ")[-1]
            ftp.do_get(file_name)
        elif data[0] == "P":
            put_file = data.strip().split(" ")[-1]
            ftp.do_put(put_file)


# 网络搭建
def main():
    sockfd = socket(AF_INET, SOCK_STREAM)
    sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sockfd.bind(ADDR)
    sockfd.listen(5)
    print("Listen the port 6712 ... ")
    while True:
        try:
            connfd, addr = sockfd.accept()
        except KeyboardInterrupt:
            sys.exit("服务器关闭")
        except Exception as e:
            print(e)
            continue
        # 创建线程处理客户端请求
        print("Connected ", addr)
        client = Thread(target=handle, args=(connfd,))
        client.setDaemon(True)
        client.start()


if __name__ == '__main__':
    main()
