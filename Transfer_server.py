import socket
import threading


def recv_size(sock, count):
    buf = ''
    while count > 0:
        newbuf = sock.recv(count).decode()
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


class transfer_server:
    def __init__(self):
        self.transfer_socket = None
        self.command_socket = None
        self.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.accept_socket.bind(('', 12346))
        self.next = False

    def connectToCS(self):
        tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp.bind(('', 12345))
        tmp.listen(10)
        first = False
        while True:
            conn, addr = tmp.accept()
            data = conn.recv(1024)
            data = data.decode()
            if data == 'transfer':
                self.transfer_socket = conn
                self.transfer_socket.setblocking(False)
                first = True
            if data == 'command' and first:
                self.command_socket = conn
                break
        print('connection to CS established')
        task = threading.Thread(target=self.recv_cmd)
        task.start()
        self.recv_cmd()

    def recv_cmd(self):
        while True:
            cmd = self.command_socket.recv(1024)
            if cmd == b'next':
                self.next = True

    def recv_data(self):
        while True:
            conn, addr = self.accept_socket.accept()
            while True:
                tmp = conn.recv(2048)
                self.transfer_socket.send(tmp)
                try:
                    tmp = self.transfer_socket.recv(2048)
                    conn.send(tmp)
                except:
                    pass
                if self.next:
                    self.next = False
                    break
            conn.close()

    def start_server(self):
        print('start server')
        self.connectToCS()


if __name__ == '__main__':
    ts = transfer_server()
    ts.start_server()
