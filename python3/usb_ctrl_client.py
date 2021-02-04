import socket
import sys
import usb_ctrl_server


def usb_ctrl_client(target_host, target_port, flag):
    # 建立一个 socket 对象（参数 AF_INET 表示标准 IPv4 地址或主机名，SOCK_STREAM 表示 TCP 客户端）
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 将客户端连接到服务器
    client.connect((target_host, target_port))

    # 向服务器发送数据
    if flag > 0:
        # 开启
        client.send(b'usbctrl f f')
    else:
        #关闭
        client.send(b'usbctrl f 0')

    # 接收返回的数据
    response = client.recv(4096)

    # 打印返回数据
    print(response)


if __name__ == "__main__":
    ip, port = usb_ctrl_server.get_usb_address(sys.argv[1:])
    usb_ctrl_client(ip, port, 1)
