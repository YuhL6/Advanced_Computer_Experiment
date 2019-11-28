import socket
import numpy
import cv2
import time
import threading
import base64

addr = ('127.0.0.1', 12345)


class MyThread(threading.Thread):
    def __init__(self, func, args=None):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        if self.args is not None:
            self.result = self.func(self.args)
        else:
            self.result = self.func()

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


def timer(limit_lime, func, args=None):
    thread = MyThread(func, args)
    ct = time.time()
    thread.setDaemon(True)
    thread.start()
    while True:
        res = thread.get_result()
        if time.time() - ct >= limit_lime or res is not None:
            return res


class Capture:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        try:
            self.sock.connect(addr)
        except:
            pass

    def camera(self):
        camera = cv2.VideoCapture(0)
        cv2.namedWindow('MyCamera')
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        while True:
            success, frame = camera.read()
            cv2.imshow('MyCamera', frame)
            cv2.imwrite('test.jpg', frame)
            if cv2.waitKey(1) & 0xff == ord(' '):
                break
            frame = cv2.imencode('.jpg', frame, encode_param)[1]
            img_data = str(base64.b64encode(frame), encoding='utf-8')
            # print(img_data)
            self.sock.send(str(len(img_data.encode())).encode())
            self.sock.send(img_data.encode())
            try:
                data = self.sock.recv(1024)
                print(data)
                if data is not None:
                    camera.release()
                    cv2.destroyWindow('MyCamera')
                    break
            except:
                continue

    def log(self, user_id):
        info = 'user_id:{}\r\n'.format(user_id)
        info += 'function:200\r\n\r\n'
        info = info.encode()
        self.sock.send(info)
        self.camera()

    def run(self):
        self.camera()


if __name__ == '__main__':
    c = Capture()
    c.run()
