from djitellopy import Tello #, TelloSwarm
import cv2
#import pygame
#import numpy as np
import time
import logging
import keyboard

# Этот класс используется для доступа к ключам словаря через точку
# Original: 
# https://bobbyhadz.com/blog/python-use-dot-to-access-dictionary#use-dot--notation-to-access-dictionary-keys-using-__dict__
class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

class DroneTracker:
    def __init__(self, drone):
        self.drone = drone
        self.drone.streamon()

        self.pid = [0.6, 0.4]
        self.previous_correction = AttributeDict({"yaw" : 0, "front" : 0})
        self.has_tracked = False
        self.loss_timestamp = 0
        self.time_to_find = 4

        self.is_searching = False
        
    def trackTarget(self, info, w, h):
        x, y = info

        if self.is_searching:
            self.searchForTarget(x)
            return

        if x < 0 and not(self.has_tracked):
            return
        
        self.has_tracked = True

        yaw_correction = x - w // 2
        front_correction = h // 2 - y

        if x < 0:
            yaw_correction = self.previous_correction.yaw * 0.99
            front_correction = self.previous_correction.front

            if self.loss_timestamp == 0:
                self.loss_timestamp = time.time() + self.time_to_find

            if self.loss_timestamp < time.time():
                print(self.loss_timestamp)
                print("LOST THE TARGET!!")
                self.reset()
                return
        else:
            self.loss_timestamp = 0

        yaw_speed = self.pid[0] * yaw_correction + self.pid[1] * (yaw_correction - self.previous_correction.yaw)
        yaw_speed = int(self.clamp(yaw_speed, -100, 100))

        front_speed = self.pid[0] * front_correction + self.pid[1] * (front_correction - self.previous_correction.front)
        front_speed = int(self.clamp(front_speed, -100, 100))

        self.drone.send_rc_control(0, front_speed, 0, yaw_speed)

        self.previous_correction.yaw   = yaw_correction
        self.previous_correction.front = front_correction

    def findTarget(self):
        self.loss_timestamp = time.time() + self.time_to_find * 2
        self.is_searching = True

    def searchForTarget(self, x):
        if x >= 0:
            print("Found target!")
            self.is_searching = False
            self.loss_timestamp = 0
            self.drone.send_rc_control(0, 0, 0, 0)
            return

        if self.loss_timestamp > time.time():
            self.drone.send_rc_control(30, 0, 30, -60)
        elif self.loss_timestamp + self.time_to_find * 2 > time.time():
            self.drone.send_rc_control(0, 0, -30, 0)
        else:
            self.is_searching = False
            self.loss_timestamp = 0
            self.drone.send_rc_control(0, 0, 0, 0)
            print("Failed to find the target!")

    def reset(self):
        self.loss_timestamp = 0
        self.previous_correction = AttributeDict({"yaw" : 0, "front" : 0})
        self.has_tracked = False
        self.drone.send_rc_control(0, 0, 0, 0)

    def print_battery_state(self):
        text = "Battery: {}%".format(self.drone.get_battery())
        print(text)

    def clamp(self, value, min_val, max_val):
        return min(max(value, min_val), max_val)


def findFace(img):
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)
    myFaceListC = []
    #myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cx = x + w // 2
        cy = y
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        myFaceListC.append([cx,cy])

    font = cv2.FONT_HERSHEY_SIMPLEX

    cv2.putText(img, "Battery: {}%".format(tello.get_battery()), (2, 236), font, 1, (255,255,255), 2, cv2.LINE_AA)
    cv2.putText(img, "Temperature: {}".format(tello.get_temperature()), (2, 200), font, 1, (255,255,255), 2, cv2.LINE_AA)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if len(myFaceListC) != 0:
        return img, myFaceListC[0]
    else:
        return img, [-1,0]

Tello.LOGGER.setLevel(logging.WARN)

screen_w, screen_h = 360, 240

tello = Tello()
tello.connect()
tello.takeoff()
tello.move_up(30)

tracker = DroneTracker(tello)
tracker.print_battery_state()

timestamp = 0

while True:
    if keyboard.is_pressed("q"):
        tello.send_rc_control(0, 0, 0, 0)
        tello.land()
        tello.streamoff()
        break

    if keyboard.is_pressed("r"):
        if not tracker.is_searching:
            tracker.findTarget()

    if keyboard.is_pressed("w"):
        tello.move_up(20)

    if keyboard.is_pressed("s"):
        tello.move_down(20)

    img = tello.get_frame_read().frame
    img = cv2.resize(img, (screen_w, screen_h))
    img, info = findFace(img)

    cv2.imshow("output", img)
    cv2.waitKey(1)

    tracker.trackTarget(info, screen_w, screen_h)

else:
    print("Произошла ебтвоюмать")