# coding=utf-8
import socket
import subprocess
import sys
import getopt


def get_usb_address(argv):
    ip = ''
    port = 0
    try:
        options, _ = getopt.getopt(argv, "hi:p:", ["ip=", "port="])
    except getopt.GetoptError:
        print('usage : usb_ctrl_server.py -i <ip> -p <port>')
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            print('usage : usb_ctrl_server.py -i <ip> -p <port>')
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
    print('get usb address', ip, port)
    if len(ip) == 0 or port == 0:
        print('usage : usb_ctrl_server.py -i <ip> -p <port>')
        sys.exit()
    return ip, port


def usb_ctrl_server(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    address = (ip, port)
    server.bind(address)
    server.listen()
    #while语句作用：（当客户端关闭后）接受新客户端的连接，实现服务端不间断地提供服务。
    while True:
        conn, _ = server.accept()
        #while语句作用：接受来自客户端的消息、打印，回复消息；当客户端的消息中包含‘bye’时，断开本次连接。
        while True:
            msg = conn.recv(1024).decode('utf-8')
            print('recv msg', msg)
            result = b'unsupport'
            if 'usbctrl' in msg:
                param = msg.split(' ')
                if len(param) != 3:
                    conn.send(b'error')
                else:
                    sh = r'USBCtrl.exe'  # 这里r可以可以不管空格和中文字符的烦恼
                    p = subprocess.Popen(sh + ' ' + param[1] + ' ' + param[2])
                    stdout, stderr = p.communicate()
                    print('result', stdout, stderr, p.returncode)
                    result = b'success'
            conn.send(result)
            print('send result ', result)
            conn.close()
            break
    server.close()


if __name__ == "__main__":
    ip, port = get_usb_address(sys.argv[1:])
    usb_ctrl_server(ip, port)
