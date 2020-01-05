import socket
import numpy
import cv2
import time
import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

import eel
from try_AES import *
import random

addr = ('122.51.26.166', 12345)

REGISTER = 0
LOG = 1
ASK_KEY = 2


def pack(user_id, rsa_enc_aes_key, data, mode):
    if mode == REGISTER:
        msg = '000 {}\r\n'.format(user_id)
        msg += '{}\r\n'.format(rsa_enc_aes_key)
        msg += '{}\r\n'.format(data)
        msg += '\r\n'
        return msg.encode()
    elif mode == LOG:
        msg = '001 {}\r\n'.format(user_id)
        msg += '{}\r\n'.format(rsa_enc_aes_key)
        msg += '{}\r\n'.format(data)
        msg += '\r\n'
        return msg.encode()
    elif mode == ASK_KEY:
        msg = '002 {}\r\n'.format('')
        msg += '{}\r\n'.format('')
        msg += '{}\r\n'.format('')
        msg += '\r\n'
        return msg.encode()


def unpack(data):
    msg = data.decode()
    msg = msg.split('\r\n')
    method_code = msg[0].split(' ')[0]
    user_id = msg[0].split(' ')[1]
    rsa_enc_aes_key = msg[1]
    data = msg[2]
    return method_code, user_id, rsa_enc_aes_key, data


def keyGen(length):
    checkcode = ''
    for i in range(length):
        if random.random() < 0.5:
            current = chr(random.randrange(65, 90))
            checkcode += str(current)
        else:
            checkcode += str(random.randint(0, 9))
    return checkcode


class Capture:
    def __init__(self, user_id, mode):
        self.user_id = user_id
        self.mode = mode
        self.capture = cv2.VideoCapture(0)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(addr)
        except:
            print('error')
        self.sock.setblocking(False)
        self.sock.send(pack('', '', '', ASK_KEY))
        while True:
            try:
                reply = self.sock.recv(1024)
                print(reply)
                break
            except:
                pass
        self.public_key = RSA.import_key(reply)

    def camera(self):
        camera = cv2.VideoCapture(0)
        camera.set(3, 640)
        camera.set(4, 480)
        cv2.namedWindow('MyCamera')
        ctime = time.time() - 0.5
        while True:
            success, frame = camera.read()
            cv2.imshow('MyCamera', frame)
            if cv2.waitKey(1) & 0xff == ord(' '):
                break
            if time.time() - ctime > 0.5:
                ctime = time.time()
                frame = frame.tolist()
                aes_key = keyGen(32)
                aes = USE_AES(aes_key)
                enc_photo = aes.encrypt(str(frame))
                cipher_rsa = PKCS1_OAEP.new(self.public_key)
                enc_key = cipher_rsa.encrypt(aes_key.encode())
                data = pack(self.user_id, enc_key, enc_photo, self.mode)
                # self.sock.send(str(len(data.decode())).encode())
                print('!')
                '''current = 0
                self.sock.setblocking(True)
                while True:
                    if current + 10000 < len(data):
                        self.sock.send(data[current:current + 10000])
                        current += 10000
                    else:
                        self.sock.send(data[current:len(data)])
                        break'''
                self.sock.setblocking(True)
                self.sock.send(data)
                time.sleep(0.1)
                self.sock.send(b'aaa')
                print(len(data))
                return 1
                self.sock.setblocking(False)
                # print(data)
                try:
                    data = self.sock.recv(1024)
                    data = unpack(data)
                    print(data)
                    if data is not None:
                        camera.release()
                        cv2.destroyWindow('MyCamera')
                        return data
                except:
                    continue
            print('return!')
            return 1

    def log(self, user_id):
        info = 'user_id:{}\r\n'.format(user_id)
        info += 'function:200\r\n\r\n'
        info = info.encode()
        self.sock.send(info)
        self.camera()

    def run(self):
        data = self.camera()
        return data


def startCamera(user_id, mode):
    c = Capture(user_id, mode)
    feedback = c.run()
    return feedback
