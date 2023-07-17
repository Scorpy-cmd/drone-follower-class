from djitellopy import Tello, TelloSwarm
import cv2
#import pygame
#import numpy as np
#import time

tello = Tello()
tello.connect()
tello.streamon()
print(tello.get_battery())

tello.takeoff()

w, h = 360, 240
required_area = 5000
pid = [0.6, 0.4]
pError = [0, 0, 0]

def clamp(value, min_val, max_val):
    return min(max(value, min_val), max_val)


def findFace(img):
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)
    myFaceListC = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        myFaceListC.append([cx,cy])
        myFaceListArea.append(area)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "Battery: {}%".format(tello.get_battery()), (2, 236), font, 0.3,(255,255,255), 1, cv2.LINE_AA)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img,[[0,0],0]


def trackFace(info, w, pid, pError):
    area = info[1]
    x, y = info[0]

    yaw_error = x - w // 2
    yaw_speed = pid[0] * yaw_error + pid[1] * (yaw_error - pError[0])
    yaw_speed = int(clamp(yaw_speed, -100, 100))

    front_error = (required_area - area) // 70
    front_speed = pid[0] * front_error + pid[1] * (front_error - pError[1])
    front_speed = int(clamp(front_speed, -100, 100))

    up_error = h // 2 - y
    up_speed = pid[0] * up_error - pid[1] * (up_error - pError[2])
    up_speed = int(clamp(up_speed, -100, 100))

    if area == 0:
        yaw_speed = 0
        front_speed = 0
        up_speed = 0

    tello.send_rc_control(0, front_speed, up_speed, yaw_speed)
    return [yaw_error, front_error, up_error]


while True:
    img = tello.get_frame_read().frame
    img = cv2.resize(img, (w,h))
    img, info = findFace(img)
    pError = trackFace(info, w , pid, pError)

    cv2.imshow("output", img)
    cv2.waitKey(1)