import socket
import numpy as np
import face_recognition


class Message:
    def __init__(self, data=[]):
        self.user_id = data[0].split(':')[-1]
        self.function = data[1].split(':')[-1]
        photo = data[2].split(':')[-1]
        

    def recognition(self, reference):
        try:
            reference = string_to_float_array(reference)
            print("r", reference)
            if len(self.face_id) == 0:
                return b"403"
            print("f", self.face_id)
            fresh = string_to_float_array(self.face_id)
            print("f", fresh)
            print(len(reference) == len(fresh))
            if calculate_distance(reference, fresh) < 0.6:
                return b"200"
            else:
                return b"404"
        except:
            return b"405"


class computation_server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        print(1)
        self.socket.connect(('122.51.26.166', 12345))
        self.socket.send(b'it\'s me')
        self.recv()

    def recv(self):
        while True:
            data = ''
            while True:
                tmp = self.socket.recv(2048)
                tmp = tmp.decode()
                print(tmp)
                data += tmp
                if tmp[len(tmp)-3: len(tmp)-1] == '\r\n':
                    break
            data = data.split('\r\n')
            print(data)
            face_vectors = face_encodings(data[2])
            if message.function == '201':
                info = message.register(data)
            elif message.function == '200':
                info = message.recognition(data)
            self.socket.send(info)


def string_to_float_array(str):
    str = str[1:len(str) - 1].split(' ')
    arr = []

    for d in str:
        if d != '' and d[-1] == '\n':
            d = d[0:len(d) - 1]
            print(d)
        if d.isprintable() and not d.isspace() and d != '':
            d = float(d)
            arr.append(d)
    return arr


def calculate_distance(data1, data2):
    sum = 0
    print("data1=", len(data1))
    print("data2=", len(data2))
    for i in range(len(data1)):
        sum = sum + (data1[i] - data2[i]) ** 2
    return sum ** (1 / 2)


if __name__ == '__main__':
    server = computation_server()
    server.connect()
