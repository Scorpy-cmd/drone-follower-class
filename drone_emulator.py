# Drone Emulator

from djitellopy import Tello
from time import sleep
import cv2
import pygame
import math
import numpy as np
import threading
from Drone import Drone
from drone_map import draw_map
from face_tracker import findFace, DroneTracker, ObjectRecognition
import datetime


# ######### PARAMETERS #########
# fSpeed = 117/10
# angularSpeed = 360 / 10
# interval = 0.25
# dInterval = fSpeed * interval
# aInterval = angularSpeed * interval
# ##############################
#
# drones = [
#     [300, 550, 0, 0],
#     [300, 350, 180, 180],
#     [200, 450, 90, 90],
#     [400, 450, 270, 270],
# ]
#
# pygame.init()
# win = pygame.display.set_mode((600, 600))
# running = True

# Checks if the button is pressed
def getKey(keyName):
    ans = False
    global running

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            should_stop = True

    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[myKey]:
        ans = True
    # pygame.display.update()

    return ans


# me = Tello()
# me.connect()
# me.streamon()
# print(me.get_battery())

# Get keyboard input for a single drone
def getKeyboardInput(drones, number):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 15
    aspeed = 50
    d = 0
    global running

    if getKey("ESCAPE"): running = False
    # elif getKey("t"): me.takeoff()
    if getKey("LEFT"):
        lr = -speed
        d = dInterval
        drones[0].set_map_pos([drones[0].get_map_pos()[0],
                               drones[0].get_map_pos()[1],
                               drones[0].get_map_pos()[2],
                               -180])
    elif getKey("RIGHT"):
        lr = speed
        d = -dInterval
        drones[0].set_map_pos([drones[0].get_map_pos()[0],
                               drones[0].get_map_pos()[1],
                               drones[0].get_map_pos()[2],
                               180])

    if getKey("UP"):
        fb = speed
        d = dInterval
        drones[0].set_map_pos([drones[0].get_map_pos()[0],
                               drones[0].get_map_pos()[1],
                               drones[0].get_map_pos()[2],
                               270])
    elif getKey("DOWN"):
        fb = -speed
        d = -dInterval
        drones[0].set_map_pos([drones[0].get_map_pos()[0],
                               drones[0].get_map_pos()[1],
                               drones[0].get_map_pos()[2],
                               -90])

    if getKey("w"):
        ud = -speed
        # curr_pos[2] += fSpeed
    elif getKey("s"):
        ud = speed
        # curr_pos[2] -= fSpeed

    if getKey("a"):
        yv = -aspeed
        drones[0].set_map_pos([drones[0].get_map_pos()[0],
                               drones[0].get_map_pos()[1],
                               drones[0].get_map_pos()[2] - aInterval,
                               drones[0].get_map_pos()[3]])
        # curr_pos[3] -= aInterval
    elif getKey("d"):
        yv = aspeed
        drones[0].set_map_pos([drones[0].get_map_pos()[0],
                               drones[0].get_map_pos()[1],
                               drones[0].get_map_pos()[2] + aInterval,
                               drones[0].get_map_pos()[3]])
        # curr_pos[3] += aInterval
    # if getKey("q"): me.land()

    sleep(interval)
    drones[0].set_map_pos([drones[0].get_map_pos()[0],
                           drones[0].get_map_pos()[1],
                           drones[0].get_map_pos()[2],
                           drones[0].get_map_pos()[3] + drones[0].get_map_pos()[2]])
    # drones[number][3] += drones[number][2]

    temp_x = int(d * np.cos(np.deg2rad(drones[0].get_map_pos()[3])))
    temp_y = int(d * np.sin(np.deg2rad(drones[0].get_map_pos()[3])))

    drones[0].set_map_pos([drones[0].get_map_pos()[0] + temp_x,
                           drones[0].get_map_pos()[1] + temp_y,
                           drones[0].get_map_pos()[2],
                           drones[0].get_map_pos()[3]])
    # drones[number][0] += temp_x
    # drones[number][1] += temp_y

    # curr_pos[0] += temp_x
    # curr_pos[1] += temp_y

    return [lr, fb, ud, yv]


def CircleFlight(tello, curr_pos):
    d = 0
    if (str(type(tello)) == "<class 'djitellopy.tello.Tello'>"):
        tello.send_rc_control(0, 0, 0, 0)
        sleep(0.1)

        tello.takeoff()
        tello.send_rc_control(0, 0, 50, 0)
        sleep(2.5)
        tello.send_rc_control(0, 0, 0, 0)

        # # Turns motors on:
        # tello.send_rc_control(-100, -100, -100, 100)
        # sleep(2)
        # tello.send_rc_control(0, 10, 20, 0)
        # sleep(3)
        # tello.send_rc_control(0, 0, 0, 0)
        # sleep(2)

        v_up = 0
        while target_wait:
            img = tello.get_frame_read().frame
            img = cv2.resize(img, (w, h))

            tello.send_rc_control(40, -5, v_up, -35)
            sleep(4)
            img, info = findFace(img)
            tello.send_rc_control(0, 0, 0, 0)
            sleep(0.5)

        return img, info
    else:
        print("Emulator mode")

        curr_pos[2] = 175

        v_up = 0
        max_val = 0
        while target_wait:
            # tello.send_rc_control(40, -5, v_up, -35)

            d = -dInterval
            drones[0][3] = 180

            drones[0][2] -= aInterval
            curr_pos[3] -= aInterval

            sleep(interval)
            drones[0][3] += drones[0][2]
            drones[0][0] += int(d * math.cos(math.radians(drones[0][3])))
            drones[0][1] += int(d * math.sin(math.radians(drones[0][3])))

            curr_pos[0] += int(d * math.cos(math.radians(drones[0][3])))
            curr_pos[1] += int(d * math.sin(math.radians(drones[0][3])))

            draw_map(drones)
            if (drones[0][0] > max_val):
                max_val = drones[0][0]
            print(max_val)
        return 0
    # # tello.send_rc_control(0, 0, 0, 0)
    # # sleep(0.1)
    # #
    # # tello.takeoff()
    # # tello.send_rc_control(0, 0, 50, 0)
    # # sleep(2.5)
    # # tello.send_rc_control(0, 0, 0, 0)
    #
    # # # Turns motors on:
    # # tello.send_rc_control(-100, -100, -100, 100)
    # # sleep(2)
    # # tello.send_rc_control(0, 10, 20, 0)
    # # sleep(3)
    # # tello.send_rc_control(0, 0, 0, 0)
    # # sleep(2)
    #
    # v_up = 0
    # for _ in range(4):
    #     tello.send_rc_control(40, -5, v_up, -35)
    #     sleep(4)
    #     tello.send_rc_control(0, 0, 0, 0)
    #     sleep(0.5)
    # return 0


if __name__ == '__main__':
    ######### PARAMETERS #########
    fSpeed = 117 / 10
    angularSpeed = 360 / 15
    interval = 0.25
    dInterval = fSpeed * interval
    aInterval = angularSpeed * interval
    ##############################
    # curr_pos = [0.0, 0.0, 0.0, 0.0]
    # drones = [
    #     [300, 550, 0, 0],
    #     [300, 350, 180, 180],
    #     [200, 450, 90, 90],
    #     [400, 450, 270, 270],
    # ]

    pygame.init()
    w, h = 800, 600

    running = True
    win = pygame.display.set_mode((w, h))

    recognize_engine = ObjectRecognition()

    if (input() == "1"):
        target_wait = True
        # tracker = DroneTracker(tello)

        # CircleFlight(0, curr_pos)

    else:
        # Main loop
        capture = cv2.VideoCapture(0)

        while running:
            start = datetime.datetime.now()
            # calc = threading.Thread(target=getKeyboardInput, args=(drones, 0)).start()
            # draw_map(drones)
            # vals = getKeyboardInput(drones, 0)
            # me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = True

            _, img = capture.read()

            img = recognize_engine.recognize(img)

            #img, info = findFace(img)

            # end time to compute the fps
            end = datetime.datetime.now()
            # show the time it took to process 1 frame
            total = (end - start).total_seconds()
            fps = f"FPS: {1 / total:.2f}"
            cv2.putText(img, fps, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 248), 8)

            img = np.rot90(img)
            img = cv2.resize(img, (h, w))
            img = np.flipud(img)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # img, info = findFace(img)

            # cv2.imshow("Image", img)
            # cv2.waitKey(1)
            img = pygame.surfarray.make_surface(img)
            win.blit(img, (0, 0))
            pygame.display.update()

            sleep(1 / 120)
            # print(vals[0], vals[1], vals[2], vals[3])
            # print(drones[0])
