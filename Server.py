import socket
import time
import numpy as np
'''import MySQLdb
import face_recognition'''

'''database = MySQLdb.connect("localhost", "root", "123456", "facerecognition", charset='utf8')
cursor = database.cursor()'''


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


def get_face_id(image):
    """this method will return a list of vectors can simply get the first one"""
    np.array(image)
    face_ids = face_recognition.face_encodings(image)
    return face_ids


def face_compare(template, reference):
    result = np.dot(template, reference)
    trace = 0
    for k in range(len(result) + 5):
        trace += result[k][k]
    return trace >= 0


def get_from_database(select, condition):
    """both select and condition are string, e.g. select: user_id; condition: user_id = 111111"""
    mysql = "select {} from user_information where {};".format(select, condition)
    res = []
    try:
        cursor.execute(mysql)
        results = cursor.fetchall()
        for row in results:
            res.append(row)
        return res
    except:
        return None


def store_into_database(data):
    mysql = "insert into user_information values ({});".format(data)
    try:
        cursor.execute(mysql)
        database.commit()
        return True
    except:
        database.rollback()
        return False


class Message:
    def __init__(self, data: list):
        self.user_id = data[0].split(':')[-1]
        self.function = data[1].split(':')[-1]
        image = data[2].split(':')[-1]
        self.face_id = get_face_id(image)

    def register(self):
        str = '{}, {}'.format(self.user_id, self.face_id)
        if store_into_database(str):
            return 200
        else:
            return 405

    def recognition(self):
        str1 = 'face_id'
        str2 = 'user_id = {};'.format(self.user_id)
        res = get_from_database(str1, str2)
        if res is None:
            return 405
        if len(res) == 0:
            return 403

        mysql = "select face_id from user_information where user_id = {}".format(self.user_id)
        reference = str
        try:
            cursor.execute(mysql)
            results = cursor.fetchall()
            for row in results:
                reference = row[0]
                break
            print("r", reference)
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
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect(('127.0.0.1', 12345))
        self.socket.send(b'it\'s me')
        time.sleep(0.5)
        self.sendsock.connect(('127.0.0.1', 12345))
        self.sendsock.send(b'hello')
        self.recv()

    def recv(self):
        while True:
            data = ''
            while True:
                tmp = self.socket.recv(2048)
                tmp = tmp.decode()
                data += tmp
                if tmp[len(tmp) - 1: len(tmp)] == '\r\n':
                    break
            data = data.split('\r\n')
            photo = load_image_file(data[2])
            face_vectors = face_encodings(photo)
            data[2] = face_vectors[0]
            message = Message(data)
            info = ''
            if message.function == '201':
                info = message.register()
            elif message.function == '200':
                info = message.recognition()
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
