# import pygame
import cv2
# import numpy as np
# from time import sleep, time
print("setting up drone")
from Drone import Drone
print("setting up tracker")
from Face_tracker import DroneTracker
print("setting up yolo")
from yolo import PersonRecognision
print("done")


def script(IP, state_port, vs_port, drone_index, arr, init_check, running):
    if drone_index != 0:
        while not init_check[drone_index - 1]:
            continue
    drone = Drone(IP,state_port, vs_port)
    init_check[drone_index] = True
    print("starting the drone...")
    startDrone(drone, drone_index, arr, running)


def startDrone(drone, drone_index, arr, running):
    tello = drone.drone
    tello.takeoff()
    tello.move_up(150)
    tello.rotate_clockwise(90 * drone_index)
    tello.move_forward(100)
    tello.rotate_clockwise(180)
    follower = DroneTracker(tello)
    tello.streamon()
    yolo = PersonRecognision()

    arr[drone_index] = True
    print("started!")
    while not_ready_to_ship(arr):
        tello.send_rc_control(0,0,0,0)

    while running:
        frame = tello.get_frame_read().frame
        frame, info = yolo.detect(frame)
        follower.trackTarget([info[0] // 2 + info[2] // 2, info[1]], 640, 480)

        font = cv2.FONT_HERSHEY_COMPLEX
        cv2.putText(frame, "Battery: {}%".format(tello.get_battery()), (2, 476), font, 1, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Temperature: {}".format(tello.get_temperature()), (2, 430), font, 1, (255,255,255), 2, cv2.LINE_AA)

        cv2.imshow("output", frame)
        cv2.waitKey(1)

    tello.send_rc_control(0, 0, 0, 0)
    tello.streamoff()
    tello.land()
    cv2.destroyAllWindows()


def not_ready_to_ship(arr):
    for i in arr:
        if not i:
            return True
    return False
