import socket


class transfer_server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None

    def accept(self):
        print('start server')
        self.socket.bind(('', 12345))
        self.socket.listen(10)
        while True:
            conn, addr = self.socket.accept()
            data = conn.recv(1024)
            print(data)
            data = data.decode()
            if data == 'it\'s me':
                self.conn = conn
                print('connection established')
                break
        self.recv()

    def recv(self):
        while True:
            conn, addr = self.socket.accept()
            data = conn.recv(1024)
            self.conn.send(data)
            data = self.conn.recv(1024)
            if data == b'200':
                conn.send(b'Successfully done')
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
