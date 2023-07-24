import cv2
import numpy as np
import threading
from time import sleep, time


def drawPoints(img, drones):
    for i in range(len(drones)):
        cv2.circle(img, (drones[i].get_map_pos()[0], drones[i].get_map_pos()[1]), 5, (0, 0, 255), thickness=cv2.FILLED)
        cv2.putText(img, f'Drone {i}: ({drones[i].get_map_pos()[0]}, {drones[i].get_map_pos()[1]}) m',
                    (drones[i].get_map_pos()[0] + 10, drones[i].get_map_pos()[1] + 30),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
        cv2.line(img, (drones[i].get_map_pos()[0], drones[i].get_map_pos()[1]),
                 (drones[i].get_map_pos()[0] + int(15 * np.sin(np.deg2rad(drones[i].get_map_pos()[2]))),
                  drones[i].get_map_pos()[1] - int(15 * np.cos(np.deg2rad(drones[i].get_map_pos()[2])))), (0, 0, 255),
                 1)


def draw_map(drones):
    img = np.zeros((600, 600, 3), np.uint8)
    drawPoints(img, drones)
    cv2.imshow("Map", img)
