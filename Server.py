import socket
import time
import base64
import numpy as np
import threading
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import MySQLdb
import face_recognition

database = MySQLdb.connect("localhost", "root", "123456", "face_recognition", charset='utf8')
cursor = database.cursor()


def string_to_float_array(str):
    str = str[1:len(str) - 1].split(' ')
    arr = []
    for d in str:
        if d != '' and d[-1] == '\n':
            d = d[0:len(d) - 1]
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


def recv_size(sock, count):
    buf = ''
    while count > 0:
        newbuf = sock.recv(count).decode()
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def dec_photo_to_frame(dec_photo):
    dec_photo = dec_photo.replace('[', '')
    dec_photo = dec_photo.replace(']', '')
    dec_photo = dec_photo.replace(',', '')
    dec_photo = dec_photo.replace('\n', '')
    arr = np.ndarray((480, 640, 3))
    li = dec_photo.split(' ')
    counter = 0
    for i in range(480):
        for j in range(640):
            for k in range(3):
                arr[i][j][k] = int(li[counter])
                counter += 1
    return arr


def arr_to_str(arr):
    li = arr.tolist()
    print(li)
    st = ''
    for s in li:
        for tmp in s:
            st += str(tmp)
            st += ' '
    return st


def str_to_arr(str: str):
    li = str.split(' ')
    for i in li:
        i = float(i)
    return np.array(li)


def face_compare(template, reference):
    result = np.dot(template, reference)
    trace = 0
    for k in range(len(result) + 5):
        trace += result[k][k]
    return trace >= 0


def get_from_database(user_id):
    mysql = "select face_id from user_info where user_id = {};".format(user_id)
    res = []
    try:
        cursor.execute(mysql)
        results = cursor.fetchall()
        for row in results:
            res.append(row)

        return res
    except:
        return None


def store_into_database(user_id, version, face_id):
    mysql = "insert into user_info values ({});".format(user_id, version, face_id)
    try:
        cursor.execute(mysql)
        database.commit()
        return True
    except:
        database.rollback()
        return False


def to_16(key):
    key = bytes(key, encoding="utf8")
    while len(key) % 16 != 0:
        key += b'\0'
    return key  # 返回bytes


class USE_AES:
    def __init__(self, key):
        if len(key) > 32:
            key = key[0:32]
        self.key = to_16(key)

    def aes(self):
        return AES.new(self.key, AES.MODE_ECB)  # 初始化加密器

    def encrypt(self, text):
        aes = self.aes()
        return str(base64.encodebytes(aes.encrypt(to_16(text))), encoding='utf8').replace('\n', '')  # 加密

    def decodeBytes(self, text):
        aes = self.aes()
        return str(aes.decrypt(base64.decodebytes(bytes(text, encoding='utf-8'))).rstrip(b'\0').decode("utf-8"))  # 解密


class MyThread(threading.Thread):
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


class computation_server:
    def __init__(self):
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.private_key = None
        self.public_key = None

    def connect(self):
        self.recvSocket.connect(('127.0.0.1', 12345))
        self.recvSocket.send(b'transfer')
        time.sleep(0.5)
        self.commandSocket.connect(('127.0.0.1', 12345))
        self.commandSocket.send(b'command')
        self.generate_RSA_key()
        self.recv()

    def generate_RSA_key(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        self.public_key = key.publickey.export_key()
        self.private_key = RSA.import_key(private_key)

    def recv(self):
        while True:
            data = ''
            while True:
                tmp = self.recvSocket.recv(2048)
                tmp = tmp.decode()
                data += tmp
                if data[len(data) - 4:] == '\r\n\r\n':
                    break
            data = data.split('\r\n')
            method_code = data[0].split(' ')[0]
            if method_code == '002':
                self.recvSocket.send(self.public_key)
                self.commandSocket.send(b'next')
            elif method_code == '000':
                encypted_AES_key = data[1]
                cipher_rsa = PKCS1_OAEP.new(self.private_key)
                AES_key = cipher_rsa.decrypt(encypted_AES_key)
                aes = USE_AES(AES_key)
                photo = aes.decodeBytes(data[2])
                frame = dec_photo_to_frame(photo)
                face_ids = face_recognition.face_encodings(frame)
                if len(face_ids) == 0:
                    continue
                user_id = data[0].split(' ')[1]
                if store_into_database(user_id, 1, arr_to_str(face_ids[0])):
                    self.recvSocket.send(b'Done')
                else:
                    self.recvSocket.send(b'Failed')
                self.commandSocket.send(b'next')
            elif method_code == '001':
                user_id = data[0].split(' ')[1]
                task = MyThread(get_from_database, (user_id,))
                task.start()
                encypted_AES_key = data[1]
                cipher_rsa = PKCS1_OAEP.new(self.private_key)
                AES_key = cipher_rsa.decrypt(encypted_AES_key)
                aes = USE_AES(AES_key)
                photo = aes.decodeBytes(data[2])
                frame = dec_photo_to_frame(photo)
                face_ids = face_recognition.face_encodings(frame)
                if len(face_ids) == 0:
                    continue
                task.join()
                reference = string_to_float_array(task.get_result())
                if calculate_distance(face_ids[0], reference) <= 0.6:
                    self.recvSocket.send(b'OK')
                else:
                    self.recvSocket.send(b'Failed')
                self.commandSocket.send(b'next')


if __name__ == '__main__':
    server = computation_server()
    server.connect()
