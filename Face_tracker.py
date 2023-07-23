import time

# Этот класс используется для доступа к ключам словаря через точку
# Original: 
# https://bobbyhadz.com/blog/python-use-dot-to-access-dictionary#use-dot--notation-to-access-dictionary-keys-using-__dict__
class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

class DroneTracker:
    def __init__(self, drone):
        # drone object 
        self.drone = drone 
        self.pid = [0.3, 0.4]
        self.previous_correction = AttributeDict({"side" : 0, "front" : 0})
        self.has_tracked = False
        self.loss_timestamp = 0
        self.time_to_find = 4
    
    # main function to track person
    def trackTarget(self, info : list[int, int], width_of_screen : int, height_of_screen : int) -> None:
        x, y = info

        # if target is not found and was not tracked then return
        if x < 0 and not(self.has_tracked):
            return
        
        # target is visible -> start tracking
        self.has_tracked = True

        # amount of pixels to travel sidewards
        side_correction = x - width_of_screen // 2
        # amount of pixels to travel forward
        front_correction = y - height_of_screen // 2

        # if we lost target (was tracked before but no longer exists)
        if x < 0:
            # set corrections to previous values to keep flying 
            side_correction = self.previous_correction.side
            front_correction = self.previous_correction.front

            # set timestamp when to stop if it was not set
            if self.loss_timestamp == 0:
                self.loss_timestamp = time.time() + self.time_to_find

            # if timestamp is lower than current time then reset a drone state to zeros
            if self.loss_timestamp < time.time():
                print("LOST THE TARGET!!")
                self.reset()
                return

        # if found a target, reset the timestamp
        if x >= 0:
            self.loss_timestamp = 0

        side_speed = self.pid[0] * side_correction + self.pid[1] * (side_correction - self.previous_correction.side)
        side_speed = int(self.clamp(side_speed, -100, 100))

        front_speed = self.pid[0] * front_correction + self.pid[1] * (front_correction - self.previous_correction.front)
        front_speed = - int(self.clamp(4 * front_speed, -100, 100))

        self.drone.send_rc_control(side_speed, front_speed, 0, 0)

        self.previous_correction.side  = side_correction
        self.previous_correction.front = front_correction

    # function to reset state of the drone to zeros
    def reset(self) -> None:
        self.loss_timestamp = 0
        self.previous_correction = AttributeDict({"side" : 0, "front" : 0})
        self.has_tracked = False
        self.drone.send_rc_control(0, 0, 0, 0)

    # secret function to check connection with the drone
    def print_battery_state(self):
        text = "Battery: {}%".format(self.drone.get_battery())
        print(text)

    # even more secret math function
    def clamp(self, value, min_val, max_val):
        return min(max(value, min_val), max_val)