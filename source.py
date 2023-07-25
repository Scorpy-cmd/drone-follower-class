import multiprocessing
import threading

# import pygame
from script import script
from time import sleep, time
from button import Menu


# drones_count = 2
drones = []
"192.168.0.113"
"192.168.0.118"
"192.168.0.136"
drones_ips = ['192.168.0.113', '192.168.0.136']#, '192.168.0.113']
drones_count = len(drones_ips)
print(">>> starting the process")


def main(loading_condition, running):
    print(">>> setting up the variables")
    arr = multiprocessing.Array('b', [False] * drones_count)
    init_check = multiprocessing.Array('b', [False] * (drones_count))
    print(">>> setting up processes")
    for i in range(drones_count):
        drones.append(threading.Thread(target=script, args=(
            drones_ips[i], 17600 + i * 11, 8080 + i * 7, i, arr, init_check, running, loading_condition, drones_count)))
        drones[i].start()
        sleep(1)

    print("joining")
    for i in range(drones_count):
        drones[i].join()


if __name__ == "__main__":
    running = multiprocessing.Array('b', [True])
    loading_condition = multiprocessing.Array('b', [False])
    start_process = multiprocessing.Process(target=Menu, args=(loading_condition, running))
    start_process.start()

    while not loading_condition[0]:
        continue
    main(loading_condition, running)
