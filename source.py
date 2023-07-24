import multiprocessing
import pygame
from script import script
from time import sleep, time

drones_count = 2
drones = []
drones_ips = ['192.168.0.118']

def main():
    arr = multiprocessing.Array('b', [False] * drones_count)
    init_check = multiprocessing.Array('b', [False] * (drones_count - 1))
    running = multiprocessing.Value("b", True)

    for i in range(drones_count):
        drones.append(multiprocessing.Process(target=script, args=(drones_ips[i], 17600 + i * 11, 8080 + i * 7, i, arr, init_check, running)))
        drones[i].start()
        sleep(1)

    for i in range(drones_count):
        drones[i].join()

if __name__ == "__main__":
    main()
