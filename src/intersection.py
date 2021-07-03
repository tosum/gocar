from car import Car, CarStatistic, Profile
from direction import Direction, directions
from copy import deepcopy
import random

class Intersection:
    def __init__(self, road_len):
        self.road_len = road_len # amount of road after the 4 center squares
        self.waiting_cars = []
        self.active_cars = []

        self.start_queues = {
            Direction.Up: [],
            Direction.Right: [],
            Direction.Down: [],
            Direction.Left: []
        }

        self.num_cars = 0
        self.time = 0
        self.crashes = 0
        self.num_finished = 0
        self.next_priority = 0

    def copy(self):
        return deepcopy(self)

    def get_start_pos(self, direction):
        small = 0
        mid1 = small + 4 * self.road_len
        mid2 = mid1 + 4
        big = mid2 + 4 * self.road_len

        if direction == Direction.Up:
            return (mid1, small)
        elif direction == Direction.Right:
            return (big, mid1)
        elif direction == Direction.Down:
            return (mid2, big)
        elif direction == Direction.Left:
            return (small, mid2)

    def get_target_pos(self, direction):
        small = 0
        mid1 = small + 4 * self.road_len
        mid2 = mid1 + 4
        big = mid2 + 4 * self.road_len

        if direction == Direction.Up:
            return (mid2, small)
        elif direction == Direction.Right:
            return (big, mid2)
        elif direction == Direction.Down:
            return (mid1, big)
        elif direction == Direction.Left:
            return (small, mid1)

    def add_car(self, from_dir, start_rest, to_dir, target_rest, profile, points):
        start_pos = self.get_start_pos(from_dir)
        target_pos = self.get_target_pos(to_dir)
        mid = 4 * self.road_len + 2

        new_car = Car(from_dir, start_rest, to_dir, target_rest, profile, points, self.num_cars, mid)
        new_car.start_pos = start_pos
        new_car.target_pos = target_pos

        self.start_queues[from_dir].append((self.time + 4 * start_rest, new_car))
        self.num_cars += 1

    def get_colliding_cars(self, pos):
        collision_range = 4

        result = []
        for car in self.active_cars:
            if abs(car.pos[0] - pos[0]) < collision_range and abs(car.pos[1] - pos[1]) < collision_range:
                result.append(car)

        return result

    def do_small_step(self, intersection_time_stats = [], 
                      no_decisions = False, ignore_crashes = False):
        # Spawn cars waiting in queues that can be spawned
        for start_dir in directions:
            if len(self.start_queues[start_dir]) == 0:
                continue

            start_pos = self.get_start_pos(start_dir)
            if len(self.get_colliding_cars(start_pos)) == 0:
                (min_car_time, min_car) = min(self.start_queues[start_dir], key = lambda p : p[0])
                if min_car_time <= self.time:
                    self.start_queues[start_dir].remove((min_car_time, min_car))
                    min_car.pos = min_car.start_pos
                    min_car.haste = random.randint(0, 5)
                    min_car.priority = self.next_priority
                    min_car.intersection_time = 0
                    self.next_priority += 1
                    self.active_cars.append(min_car)

        # Handle crashes
        crashed = []
        if not ignore_crashes:
            crashed_cars = set()
            for car in self.active_cars:
                colliding = self.get_colliding_cars(car.pos)
                if len(colliding) > 1:
                    for c in colliding:
                        crashed_cars.add(c)

            for colliding_car in crashed_cars:
                self.crashes += 1
                crashed.append(colliding_car.car_id)
                self.active_cars.remove(colliding_car)

        # Every full tick let all cars decide their next speed
        if self.time % 4 == 0 and not no_decisions and len(self.active_cars) > 0:
            self.do_step_decisions()
            
        # Every 2 ticks haste of all frustrated drivers increases
        # This represents their raising frustration
        if self.time % 8 == 0:
            for car in self.active_cars:
                if car.profile == Profile.Frustrated:
                    car.haste = min(car.haste + 1, 5)

        # Move cars and increase their time in the intersection
        for car in self.active_cars:
            car.do_small_step()
            car.intersection_time += 1

        # Handle cars that reached their targets
        new_active_cars = []
        for car in self.active_cars:
            if car.pos == car.target_pos:
                stat = CarStatistic(car)
                intersection_time_stats.append((stat, car.intersection_time / 4))

                if car.returning:
                    # A car went one way and back - it has finished
                    self.num_finished += 1
                    continue

                next_start_time = self.time + 4 * car.target_rest

                car.start_dir, car.target_dir = car.target_dir, car.start_dir
                car.start_rest, car.target_rest = car.target_rest, car.start_rest

                car.start_pos = self.get_start_pos(car.start_dir)
                car.target_pos = self.get_target_pos(car.target_dir)
                car.speed = 0

                car.returning = True

                self.start_queues[car.start_dir].append((next_start_time, car))
            else:
                new_active_cars.append(car)

        self.active_cars = new_active_cars

        self.time += 1

        return crashed

    def do_step_decisions(self):
        # Do priority trading
        for car in self.active_cars:
            car.trade_priorities(self.active_cars)

        # Sort cars by priority
        # Cars with better priority get to make decisions first
        self.active_cars.sort(key = lambda c : c.priority)

        # Give car with the highes priority the best speed possible
        # Find car with the highest priority
        priority_car = min(self.active_cars, key = lambda car : car.priority)

        # Try setting speed to -1, 0, +1
        speeds = [priority_car.speed]
        if priority_car.speed != 0:
            speeds.append(priority_car.speed - 1)
        
        if priority_car.speed != 3:
            speeds.append(priority_car.speed + 1)

        # For each speed check if other cars can find good speeds for themselves
        ok_speeds = []
        active_cars_backup = self.active_cars.copy()
        for speed in speeds:
            priority_car.speed = speed
            is_speed_ok = True

            for car in self.active_cars:
                if car.car_id != priority_car.car_id:
                    change_res = car.change_speed(self)
                    if not change_res:
                        is_speed_ok = False

            self.active_cars = active_cars_backup.copy()

            if is_speed_ok:
                ok_speeds.append(speed)

        if len(ok_speeds) > 0:
            # If we found a good speed for the highest priority car then use it
            priority_car.speed = max(ok_speeds)
        else:
            # Otherwise make the highest priority car slow down
            priority_car.speed = min(speeds)

        # After setting the highest priority car make other cars choose speed for real
        for car in self.active_cars:
            if car.car_id != priority_car.car_id:
                change_res = car.change_speed(self)

