from Drone import Drone
import pygame
import cv2
import numpy as np
from time import sleep, time
from face_tracker import DroneTracker

FPS = 120
w, h = 800, 600


def script(IP, state_port, vs_port, drone_index, arr, init_check, running):
    if drone_index != 1:
        while not init_check[drone_index - 1]:
            continue
    drone = Drone(IP,state_port, vs_port)
    init_check[drone_index] = True

    startDrone(drone, drone_index, arr, running)

def startDrone(drone, drone_index, arr, running):
    tello = drone.drone
    tello.takeoff()
    tello.move_up(80 + 5 * drone_index)
    tello.rotate_clockwise(90 * drone_index)
    tello.move_forward(50)
    tello.rotate_clockwise(180)
    follower = DroneTracker(tello)
    tello.streamon()
    arr[drone_index] = True

    while not_ready_to_ship(arr):
        tello.send_rc_control(0,0,0,0)

    while running:
        frame = tello.get_frame_read().frame

        follower.trackTarget(info, 640, 480)

    tello.send_rc_control(0, 0, 0, 0)
    tello.streamoff()
    tello.land()
    cv2.destroyAllWindows()


def main_drone(drone, w, h, arr):
    running = True
    Start = pygame.image.load("Resource/Sprites/Start.png")
    Background1 = pygame.image.load("Resource/Sprites/CyberBackground.png")
    Loading_Text = pygame.image.load("Resource/Sprites/Text_Loading.png")

    # screen.blit(Background1, (0, 0))
    # screen.blit(Loading_Text, (w / 2 - 350, h / 2 - 175))
    # pygame.display.update()

    drone.drone.takeoff()
    drone.drone.move_up(50)
    drone.drone.move_right(25)
    drone.drone.move_up(20)

    pygame.init()
    screen = pygame.display.set_mode([w, h])
    pygame.display.set_caption("Tello")
    while running:
        img = drone.get_tello().get_frame_read().frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    save_picture(img)
                    sleep(0.1)

        text = "Battery: {}%".format(drone.get_tello().get_battery())
        cv2.putText(img, text, (5, 720 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if arr[1] == True and arr[2] == True and arr[3] == True:
            screen.blit(Start, (w / 2 + 150, h / 2 + 100))
            pressed(pygame.mouse.get_pos(), arr)

        img = np.rot90(img)
        img = cv2.resize(img, (w, h))
        img = np.flipud(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = pygame.surfarray.make_surface(img)
        screen.blit(img, (0, 0))
        pygame.display.update()
        sleep(1 / FPS)

        while ready_to_ship(arr):
            follow_target(drone, w, h, screen)
            running = False
            break
    drone.get_tello().land()
    drone.get_tello().streamoff()
    drone.get_tello().end()


def save_picture(frame_read):
    cv2.imwrite(f'Images/{time.time()}.png', frame_read)


def not_ready_to_ship(arr):
    for i in arr:
        if not i:
            return True
    return False


def pressed(mouse, arr):
    click = pygame.mouse.get_pressed()
    if w / 2 - 150 < mouse[0] < w / 2 - 150 + 280:
        if h / 2 - 100 < mouse[1] < h / 2 - 100 + 190:
            if click[0] == 1:
                pygame.time.delay(200)
                print("Loading")
                arr[0] = True


def sub_drone(drone, drone_index, arr):
    running = True
    if drone_index == 2:
        drone.drone.takeoff()
        drone.drone.move_up(70)
        drone.drone.move_forward(30)
        drone.drone.move_right(25)

        arr[drone_index - 1] = True
        while running:
            while ready_to_ship(arr):
                follow_target(drone, None)
                running = False
                break
    elif drone_index == 3:
        drone.drone.takeoff()
        drone.drone.move_up(50)
        drone.drone.move_forward(35)
        drone.drone.rotate_clockwise(90)
        drone.drone.move_up(20)

        arr[drone_index - 1] = True
        while running:
            while ready_to_ship(arr):
                follow_target(drone, None)
                running = False
                break
    elif drone_index == 4:
        drone.get_tello().takeoff()
        drone.get_tello().move_right(50)
        drone.get_tello().move_forward(35)
        drone.get_tello().rotate_clockwise(-90)
        drone.get_tello().move_up(70)

        arr[drone_index - 1] = True
        while running:
            while ready_to_ship(arr):
                follow_target(drone, None)
                running = False
                break
    else:
        print("An error has occurred. Code: 1")

    drone.get_tello().land()
    drone.get_tello().streamoff()
    drone.get_tello().end()
