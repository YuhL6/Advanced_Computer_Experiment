import base64
import eel
import socket
import cv2
from api import load_image_file
from api import face_encodings
from client import *

eel.init('')


@eel.expose
def takePhoto(user_id, mode):
    feedback = startCamera(user_id, mode)
    eel.alert_feedback(feedback)


eel.start('camera2.html', mode='chrome', size=(1000, 1000))
