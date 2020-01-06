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
        self.accept_socket.bind(('', 12345))
        self.queue = []
        self.next = False
        self.both = False

    def connectToCS(self):
        self.accept_socket.listen(10)
        first = False
        while True:
            conn, addr = self.accept_socket.accept()
            data = conn.recv(1024)
            data = data.decode()
            if data == 'transfer':
                self.transfer_socket = conn
                first = True
            if data == 'command' and first:
                self.command_socket = conn
                break
        print('connection to CS established')
        task = threading.Thread(target=self.recv_cmd)
        task.start()
        task1 = threading.Thread(target=self.send_data)
        task1.start()
        self.recv_data()

    def recv_cmd(self):
        while True:
            cmd = self.command_socket.recv(2048)
            if cmd == b'next':
                self.next = True

    def recv_data(self):
        while True:
            conn, addr = self.accept_socket.accept()
            task = threading.Thread(target=self.transfer_recv, args=(conn,))
            task.start()
            while True:
                tmp = conn.recv(2048)
                self.queue.append(tmp)
                if self.next:
                    self.queue = []
                    if self.both:
                        self.both = False
                        self.next = False
                    else:
                        self.both = True
                    break
            conn.close()

    def send_data(self):
        while True:
            if len(self.queue) == 0:
                continue
            msg = self.queue[0]
            del self.queue[0]
            self.transfer_socket.send(msg)

    def transfer_recv(self, conn):
        while True:
            tmp = self.transfer_socket.recv(2048)
            conn.send(tmp)
            if self.next:
                if self.both:
                    self.both = False
                    self.next = False
                else:
                    self.both = True
                return

    def start_server(self):
        print('start server')
        self.connectToCS()


if __name__ == '__main__':
    ts = transfer_server()
    ts.start_server()
