import socket


def recv_size(sock, count):
    buf = ''
    while count > 0:
        newbuf = sock.recv(count).decode()
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


class Message:
    def __init__(self, data: str):
        data = data.split('\r\n')
        self.user_id = data[0].split(':')[-1]
        self.function = int(data[1].split(':')[-1])


class transfer_server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvS = None
        self.sendS = None

    def accept(self):
        print('start server')
        self.socket.bind(('', 12345))
        self.socket.listen(10)
        First = False
        while True:
            conn, addr = self.socket.accept()
            data = conn.recv(1024)
            print(data)
            data = data.decode()
            if data == 'it\'s me':
                self.recvS = conn
                First = True
            if data == 'hello' and First:
                self.sendS = conn
                self.sendS.setblocking(False)
                break
        self.recv()

    def recv(self):
        while True:
            conn, addr = self.socket.accept()
            data = ''
            while True:
                tmp = conn.recv(2048)
                tmp = tmp.decode()
                data += tmp
                if tmp[len(tmp) - 3: len(tmp) - 1] == '\r\n':
                    break
            self.sendS.send(data)
            message = Message(data)
            if message.function == 200:
                while True:
                    data = conn.recv(16)
                    self.sendS.send(data)
                    data = int(data.decode())
                    data = recv_size(conn, data).encode()
                    self.sendS.send(data)
            if message.function == 201:
                while True:
                    data = conn.recv(16)
                    self.sendS.send(data)
                    data = int(data.decode())
                    data = recv_size(conn, data).encode()
                    self.sendS.send(data)
                    try:
                        data = self.recvS.recv(1024)
                        conn.send(data)
                    except:
                        continue

            elif data == b'403':
                conn.send(b'No face recognized')
            elif data == b'404':
                conn.send(b'Not the same person')
            elif data == b'405':
                conn.send(b'User id not exists')
            conn.close()

    def start_server(self):
        self.accept()


if __name__ == '__main__':
    ts = transfer_server()
    ts.start_server()
