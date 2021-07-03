import random
from enum import Enum
import math
from copy import deepcopy

class CrashError(Exception):
    pass

class Profile(Enum):
    Righteous = 0,  # Green
    Hoarder = 1,    # Yellow
    Nervous = 2,    # Red
    Frustrated = 3, # Orange
    Altruistic = 4  # Blue

profiles = [
    Profile.Righteous,
    Profile.Hoarder,
    Profile.Nervous,
    Profile.Frustrated,
    Profile.Altruistic
]

class CarStatistic:
    def __init__(self, car):
        self.speed = car.speed
        self.from_dir = car.start_dir
        self.to_dir = car.target_dir
        self.haste = car.haste
        self.profile = car.profile

class Car:
    def __init__(self, start_dir, start_rest, target_dir, target_rest, profile, points, car_id, mid):
        self.car_id = car_id
        self.start_dir = start_dir
        self.target_dir = target_dir

        self.start_pos = (0, 0)
        self.target_pos = (0, 0)
        self.start_rest = start_rest # Time spent at the start
        self.target_rest = target_rest # Time spent at the target
        # start and target get swapped once a car reaches its destination
        
        self.mid = mid
        self.haste = random.randint(0, 5)
        self.priority = 1000000000
        self.profile = profile
        self.points = points

        self.pos = self.start_pos
        self.speed = 0

        self.returning = False
        
        if self.profile == Profile.Righteous:
            self.color = (51, 204, 51) # Green
        
        if self.profile == Profile.Hoarder:
            self.color = (255, 255, 102) # Yellow

        if self.profile == Profile.Nervous:
            self.color = (255, 0, 0) # Red

        if self.profile == Profile.Frustrated:
            self.color = (255, 102, 0) # Orange

        if self.profile == Profile.Altruistic:
            self.color = (51, 153, 255) # Blue

        brightness = 0.8
        self.color = (self.color[0] * brightness, self.color[1] * brightness, self.color[2] * brightness)

        self.intersection_time = 0

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

    # Here each car agent decides their next speed
    def change_speed(self, intersection):
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
                cur_intersection = intersection.copy()

                for car in cur_intersection.active_cars:
                        if car.car_id == self.car_id:
                            car.speed = cur_speed   

                steps_to_check = 3
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

        self.speed = new_speed

        return len(ok_speeds) > 0
        
    # Here the agent negotiates with other agents to swap priority for points
    def trade_priorities(self, cars):
        # First check if we need to trade priority
        if not self.want_to_trade() or self.points == 0:
            return

        # Simulate running each car and see if they would collide with me
        cars_copy = deepcopy(cars)
        my_car = None
        for car in cars_copy:
            if car.car_id == self.car_id:
                my_car = car
                break

        colliding_cars = []
        for _ in range(5):
            # My car always accelerates in the simulation
            my_car.speed = min(my_car.speed + 1, 3)
            for _ in range(4):
                for car in cars_copy:
                    car.do_small_step()
                    if car.car_id != self.car_id and abs(car.pos[0] - my_car.pos[0]) < 4 or abs(car.pos[1] - my_car.pos[1]) < 4:
                        colliding_cars.append(car)
        
        # To be first my priority would have to be lower than any of the colliding cars
        priority_to_beat = 100000000000000
        for car in colliding_cars:
            priority_to_beat = min(car.priority, priority_to_beat)

        possible_trades = [] # [(car, price)]
        for car in cars:
            self.try_trading(car, possible_trades)

        # We want to find a trade with the lowest price that beats priority_to_beat
        # If that is not possible we want the lowest priority possible
        best_car = None
        best_price = None
        for (car, price) in possible_trades:
            if best_car is None:
                best_car = car
                best_price = price
                continue

            if car.priority < priority_to_beat and price < best_price:
                best_car = car
                best_price = price
                continue

            if best_car.priority >= priority_to_beat and car.priority < best_car.priority:
                best_car = car
                best_price = price
                continue

        # Couldnt trade
        if best_car is None:
            return

        # Perform the trade
        # Swap priorities and pay the price
        self.priority, best_car.priority = best_car.priority, self.priority
        self.points -= best_price
        best_car.points += best_price

    # TODO: Do these in CLIPS?
    def want_to_trade(self):
        # Nervous always wants to go first
        if self.profile == Profile.Nervous:
            return True

        # Others want to go first if in a lot of hurry
        if self.haste == 5:
            return True

        # Altruistic and Hoarder don't want to go first if not in a lot of hurry
        if self.profile == Profile.Altruistic or self.profile == Profile.Hoarder:
            return False

        # Righteous abd Frustrated want to go first if in hurry
        if self.haste > 3:
            return True

        return False

    def try_trading(self, other, possible_trades):
        # Check if we want to trade with this car
        if other.priority > self.priority:
            return

        # Dont trade with cars coming from the same direction
        if other.start_dir == self.start_dir:
            return
        
        # Calculate the price and check if we can afford it
        price = math.ceil((other.priority - self.priority) / 2)

        # Altruistic wants to let everyone go so its prices are lower
        # But not 0 to not block the intersection
        if other.profile == Profile.Altruistic:
            price = math.ceil(price / 2)

        if price > self.points:
            return

        # Check if the other car wants to trade priorities with us

        # Righteous only lets someone with higher haste
        # Frustrated does the same, but their haste increases over time
        if other.profile == Profile.Righteous or other.profile == Profile.Frustrated:
            if self.haste <= other.haste:
                return

        # Hoarder and Altruistic let go unless in a lot of hurry
        if other.profile == Profile.Hoarder or other.profile == Profile.Altruistic:
            if other.haste == 5:
                return
        
        # Nervous never lets someone go
        if other.profile == Profile.Nervous:
            return

        # Ok we can trade
        possible_trades.append((other, price))