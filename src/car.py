import random
from enum import Enum

class CrashError(Exception):
    pass

class Profile(Enum):
    Righteous = 0,  # Green
    Hoarder = 1,    # Yellow
    Nervous = 2,    # Orange
    Frustrated = 3, # Red
    Altruistic = 4  # Blue

class CarStatistic:
    def __init__(self, car):
        self.speed = car.speed
        self.from_dir = car.start_dir
        self.to_dir = car.target_dir
        self.haste = car.haste

class Car:
    def __init__(self, car_id, start_dir, target_dir, start_rest, target_rest, mid):
        self.car_id = car_id
        self.start_dir = start_dir
        self.target_dir = target_dir

        self.start_pos = (0, 0)
        self.target_pos = (0, 0)
        self.start_rest = start_rest # Time spent at the start
        self.target_rest = target_rest # Time spent at the target
        # start and target get swapped once a car reaches its destination
        
        self.mid = mid
        self.haste = 0
        self.profile = Profile.Righteous

        self.pos = self.start_pos
        self.speed = 0

        self.returning = False
        
        random.seed(car_id)
        self.color = (random.randrange(0, 200), random.randrange(0, 200), random.randrange(0, 200))
        random.seed()

    def next_pos(self):
        move_x = 1
        if self.pos[0] > self.target_pos[0]:
            move_x = -move_x

        move_y = 1
        if self.pos[1] > self.target_pos[1]:
            move_y = -move_y
        
        if self.pos == self.target_pos:
            oob = 10000 * (self.car_id + 1)
            self.target_pos = (oob, oob)
            return (oob, oob)

        if self.pos[0] == self.target_pos[0]:
            return (self.pos[0], self.pos[1] + move_y)

        if self.pos[1] == self.target_pos[1]:
            return (self.pos[0] + move_x, self.pos[1])

        if abs(self.pos[0] - self.mid) == 2 and self.pos[0] == self.start_pos[0]:
            return (self.pos[0], self.pos[1] + move_y)

        if abs(self.pos[1] - self.mid) == 2 and self.pos[1] == self.start_pos[1]:
            return (self.pos[0] + move_x, self.pos[1])

    def do_small_step(self):
        for _ in range(self.speed):
            self.pos = self.next_pos()

    # Here each car agent decides what to do next
    def change_speed(self, intersection, stalemate = False):
        speeds = []

        if self.speed != 0:
            speeds.append(self.speed - 1)

        speeds.append(self.speed)

        if self.speed != 3:
            speeds.append(self.speed + 1)

        ok_speeds = []
        for cur_speed in speeds:
            crash = False

            try:
                for i in range(len(intersection.active_cars) + 1):
                    cur_intersection = intersection.copy()

                    if i < len(cur_intersection.active_cars):
                        s = cur_intersection.active_cars[i].speed
                        cur_intersection.active_cars[i].speed = max(0, s - 1)

                    for car in cur_intersection.active_cars:
                        if car.car_id == self.car_id:
                            car.speed = cur_speed   

                    steps_to_check = 1 if stalemate else 5
                    for _ in range(steps_to_check * 4):
                        cur_intersection.do_small_step(no_decisions = True, ignore_crashes = True)
                        
                        for car in cur_intersection.active_cars:
                            if car.car_id == self.car_id:
                                if len(cur_intersection.get_colliding_cars(car.pos)) > 1:
                                    raise CrashError()
            except CrashError:
                continue
        
            ok_speeds.append(cur_speed)

        new_speed = max(0, self.speed - 1)

        if len(ok_speeds) > 0:
            new_speed = max(ok_speeds)

        #print(ok_speeds)
        self.speed = new_speed
        
        