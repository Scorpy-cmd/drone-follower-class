from djitellopy import Tello, TelloSwarm
import cv2
import pygame
import numpy as np
from time import sleep, time
import math
from drone_map import draw_map

# Speed of the drone

S = 60
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.

FPS = 120

class DroneControl(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations (yaw)
            - W and S: Up and down.
    """

    def __init__(self):
        # Init pygame
        pygame.init()

        # Creat pygame window
        pygame.display.set_caption("Tello")
        self.screen = pygame.display.set_mode([1280, 720])

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        self.curr_pos = [0.0, 0.0, 0.0, 0.0]

        ######### PARAMETERS #########
        self.fSpeed = 117 / 10
        self.angularSpeed = 360 / 10
        self.interval = 0.25
        self.dInterval = self.fSpeed * self.interval
        self.aInterval = self.angularSpeed * self.interval

        self.drones = [
            [300, 550, 0, 0],
            [300, 350, 180, 180],
            [200, 450, 90, 90],
            [400, 450, 270, 270],
        ]
        ##############################

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False

        # create update timer
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

    def run(self):

        self.tello.connect()
        self.tello.set_speed(self.speed)

        # In case streaming is on. This happens when we quit this program without the escape key.
        self.tello.streamoff()
        self.tello.streamon()

        frame_read = self.tello.get_frame_read()

        should_stop = False
        while not should_stop:

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    elif event.key == pygame.K_p:
                        self.save_picture(frame_read)
                        time.sleep(0.3)
                    else:
                        self.keydown(event.key, 0)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if frame_read.stopped:
                break

            self.screen.fill([0, 0, 0])

            frame = frame_read.frame
            # battery n
            text = "Battery: {}%".format(self.tello.get_battery())
            cv2.putText(frame, text, (5, 720 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            frame = np.rot90(frame)
            frame = cv2.resize(frame, (1280, 720))
            frame = np.flipud(frame)

            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()

            draw_map(self.drones)

            time.sleep(1 / FPS)

        # Call it always before finishing. To deallocate resources.
        self.tello.end()

    def keydown(self, key, number):
        aspeed = 50
        d = 0
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP:  # set forward velocity
            self.for_back_velocity = S
            d = self.dInterval
            self.drones[number][3] = 270
        elif key == pygame.K_DOWN:  # set backward velocity
            self.for_back_velocity = -S
            d = - self.dInterval
            self.drones[number][3] = -90
        elif key == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -S
            d = self.dInterval
            self.drones[number][3] = -180
        elif key == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = S
            d = - self.dInterval
            self.drones[number][3] = 180
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = S
            self.curr_pos[2] += self.fSpeed
        elif key == pygame.K_s:  # set down velocity
            self.up_down_velocity = -S
            self.curr_pos[2] -= self.fSpeed
        elif key == pygame.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -S
            self.drones[number][2] -= self.aInterval
            self.curr_pos[3] -= self.aInterval
        elif key == pygame.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = S
            self.drones[number][2] += self.aInterval
            self.curr_pos[3] += self.aInterval


        sleep(self.interval)
        self.drones[number][3] += self.drones[number][2]
        self.drones[number][0] += int(d * math.cos(math.radians(self.drones[number][3])))
        self.drones[number][1] += int(d * math.sin(math.radians(self.drones[number][3])))

        self.curr_pos[0] += int(d * math.cos(math.radians(self.drones[number][3])))
        self.curr_pos[1] += int(d * math.sin(math.radians(self.drones[number][3])))

    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  # land
            not self.tello.land()
            self.send_rc_control = False

    def update(self):
        """ Update routine. Send velocities to Tello.
        """
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
                self.up_down_velocity, self.yaw_velocity)

    def save_picture(self, frame_read):
        cv2.imwrite(f'Images/{time.time()}.png', frame_read.frame)


def main():
    drone = DroneControl()

    # run frontend
    drone.run()


if __name__ == '__main__':
    main()