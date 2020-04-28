"""
    ftp文件传输客户端
"""
from socket import *
import sys

HOST = "127.0.0.1"
PORT = 6712
ADDR = (HOST, PORT)


# 具体功能
class FtpClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L")  # 发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            # 接收文件列表
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("谢谢使用")

    def do_get(self, file_name):
        self.sockfd.send("G ".encode() + file_name.encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            fd = open(file_name, "wb")
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                fd.write(data)
            fd.close()
            print("文件下载成功")
        else:
            print(data)

    def do_put(self, file_name):
        try:
            f = open(file_name, "rb")
        except Exception:
            print("没有该文件")
            return
        fd_name = file_name.split("\\")[-1]
        self.sockfd.send("P ".encode() + fd_name.encode())
        data = self.sockfd.recv(128).decode()
        if data == "Error":
            print("文件已存在，上传失败！")
            return
        elif data == "OK":
            fd = open(file_name, "rb")
            while True:
                data = fd.read(1024)
                if not data:
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
            fd.close()
            print("上传成功")


def request(sockfd):
    ftp = FtpClient(sockfd)
    while True:
        print("\n==============命令选项==============")
        print("--------------- list ---------------")
        print("------------- get file -------------")
        print("------------- put file -------------")
        print("--------------- quit ---------------")
        print("====================================")

        cmd = input("输入命令：")
        if cmd == "list":
            ftp.do_list()
        elif cmd.strip() == "quit":
            ftp.do_quit()
        elif cmd[:3] == "get":
            file_name = cmd.strip().split(" ")[-1]
            ftp.do_get(file_name)
        elif cmd[:3] == "put":
            new_file = input("输入文件路径：")
            ftp.do_put(new_file.strip())


# 网络连接
def main():
    sockfd = socket(AF_INET, SOCK_STREAM)
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print("连接服务器失败")
        return
    else:
        print("""
                        ****************************************
                            1. Data     2. File     3. Image
                        ****************************************
        """)
        cls = input("请选择文件种类:")
        if cls not in ["Data", "File", "Image"]:
            print("Sorry input Error!!")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)  # 发送具体请求


if __name__ == '__main__':
    main()
