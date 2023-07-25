import logging
from djitellopy import Tello
import multiprocessing


class Drone:
    def __init__(self, IP, state_port, vs_port):
        self.CurPos = [0, 0, 0, 0]
        # self.MapPos = MapPos

        self.IP = IP
        self.state_port = state_port
        self.vs_port = vs_port
        # self.drone = Tello(host=IP, vs_udp=vs_port)
        # self.drone.LOGGER.setLevel(logging.WARN)
        # self.drone.connect()
        # self.drone.set_network_ports(state_port, vs_port)
        self.drone = None
        process = multiprocessing.Process(target=self.connect_switch_port())
        process.start()
        process.join()
        process.kill()


    def connect_switch_port(self):
        self.drone = Tello(host=self.IP, vs_udp=self.vs_port)
        self.drone.LOGGER.setLevel(logging.WARN)
        self.drone.connect()
        self.drone.set_network_ports(self.state_port, self.vs_port)

        self.drone.set_video_fps(Tello.FPS_30)
        self.drone.set_video_resolution(Tello.RESOLUTION_480P)
        self.drone.set_video_bitrate(Tello.BITRATE_1MBPS)