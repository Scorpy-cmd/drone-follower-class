# import pygame
import cv2
import multiprocessing
# import numpy as np
from time import sleep
print("setting up drone")
from Drone import Drone
print("setting up tracker")
from Face_tracker import DroneTracker
print("setting up yolo")
from yolo import PersonRecognision
print("done")


def script(IP, state_port, vs_port, drone_index, arr, init_check, running, loading_condition, drones_count):
    if drone_index != 0:
        while not init_check[drone_index - 1]:
            continue
    drone = Drone(IP,state_port, vs_port)
    #loading_condition[0] = False
    init_check[drone_index] = True
    print("starting the drone...")

    # processes = []
    # for i in range(drones_count):
    #     processes.append(multiprocessing.Process(target=startDrone,
    #                         args=(drone, drone_index, arr, running, loading_condition)))
    #     processes[drone_index - 1].start()
    #     sleep(1)
    startDrone(drone, drone_index, arr, running, loading_condition)
    # for i in range(drones_count):
    #     processes[i].join()


def startDrone(drone, drone_index, arr, running, loading_condition):
    tello = drone.drone
    tello.takeoff()
    tello.move_up(150)
    tello.rotate_clockwise(90 * drone_index)
    tello.move_forward(150)
    tello.rotate_clockwise(180)
    loading_condition[0] = False
    follower = DroneTracker(tello)
    tello.streamon()
    yolo = PersonRecognision()

    arr[drone_index] = True
    print("started!")
    while not_ready_to_ship(arr):
        tello.send_rc_control(0,0,0,0)

    if drone_index == 0:
        while running:
            # tello.send_rc_control(0, 0, 0, 0)
            # continue
            state = multiprocessing.Array('b', [True])
            frame = tello.get_frame_read().frame
            frame, info = yolo.detect(frame)
            follower.trackTarget([info[0] // 2 + info[2] // 2, info[1]], 640, 480)

            font = cv2.FONT_HERSHEY_COMPLEX
            cv2.putText(frame, "Battery: {}%".format(tello.get_battery()), (2, 476), font, 1, (255, 255, 255), 2,
                        cv2.LINE_AA)
            cv2.putText(frame, "Temperature: {}".format(tello.get_temperature()), (2, 430), font, 1, (255, 255, 255), 2,
                        cv2.LINE_AA)
            cv2.imshow("output" + str(drone_index), frame)
            cv2.waitKey(1)
            # process1 = multiprocessing.Process(target=screen_cast, args=(frame, drone_index, state))
            # process1.start()
            # while state[0]:
            #     continue
    if drone_index == 1:

        while running:
            # tello.send_rc_control(0, 0, 0, 0)
            # continue
            state1 = multiprocessing.Array('b', [True])
            frame1 = tello.get_frame_read().frame
            frame1, info = yolo.detect(frame1)
            follower.trackTarget([info[0] // 2 + info[2] // 2, info[1]], 640, 480)

            font = cv2.FONT_HERSHEY_COMPLEX
            cv2.putText(frame1, "Battery: {}%".format(tello.get_battery()), (2, 476), font, 1, (255, 255, 255), 2,
                        cv2.LINE_AA)
            cv2.putText(frame1, "Temperature: {}".format(tello.get_temperature()), (2, 430), font, 1, (255, 255, 255), 2,
                        cv2.LINE_AA)
            cv2.imshow("output" + str(drone_index), frame1)
            cv2.waitKey(1)
            # process1 = multiprocessing.Process(target=screen_cast, args=(frame1, drone_index, state1))
            # process1.start()
            # while state1[0]:
            #     continue
    # while running:
    #     # tello.send_rc_control(0, 0, 0, 0)
    #     # continue
    #
    #     frame = tello.get_frame_read().frame
    #     frame, info = yolo.detect(frame)
    #     follower.trackTarget([info[0] // 2 + info[2] // 2, info[1]], 640, 480)
    #
    #     font = cv2.FONT_HERSHEY_COMPLEX
    #     cv2.putText(frame, "Battery: {}%".format(tello.get_battery()), (2, 476), font, 1, (255,255,255), 2, cv2.LINE_AA)
    #     cv2.putText(frame, "Temperature: {}".format(tello.get_temperature()), (2, 430), font, 1, (255,255,255), 2, cv2.LINE_AA)
    #
    #     cv2.imshow("output" + str(drone_index), frame)
    #     cv2.waitKey(1)

    tello.send_rc_control(0, 0, 0, 0)
    tello.streamoff()
    tello.land()
    cv2.destroyAllWindows()


def screen_cast(image, drone_index, state):
    while True:
        cv2.imshow("output" + str(drone_index), image)
        cv2.waitKey(1)


def not_ready_to_ship(arr):
    for i in arr:
        if not i:
            return True
    return False
