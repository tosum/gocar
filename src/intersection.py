from car import Car
from direction import Direction, directions
from copy import deepcopy

class CarCrashException(Exception):
    pass

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

    def add_car(self, from_dir, to_dir, start_rest, target_rest):
        start_pos = self.get_start_pos(from_dir)
        target_pos = self.get_target_pos(to_dir)
        mid = 4 * self.road_len + 2

        new_car = Car(self.num_cars, from_dir, to_dir, start_rest, target_rest, mid)
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

    def do_small_step(self, no_decisions = False, ignore_crashes = False):
        for start_dir in directions:
            if len(self.start_queues[start_dir]) == 0:
                continue

            start_pos = self.get_start_pos(start_dir)
            if len(self.get_colliding_cars(start_pos)) == 0:
                (min_car_time, min_car) = min(self.start_queues[start_dir], key = lambda p : p[0])
                if min_car_time <= self.time:
                    self.start_queues[start_dir].remove((min_car_time, min_car))
                    min_car.pos = min_car.start_pos
                    self.active_cars.append(min_car)

        crash = False
        if not ignore_crashes:
            crashed_cars = set()
            for car in self.active_cars:
                colliding = self.get_colliding_cars(car.pos)
                if len(colliding) > 1:
                    for c in colliding:
                        crashed_cars.add(c)

            for colliding_car in crashed_cars:
                self.crashes += 1
                self.active_cars.remove(colliding_car)
                crash = True

        if self.time % 4 == 0 and not no_decisions:
            stalemate = True
            for car in self.active_cars:
                car.change_speed(self)
                if car.speed != 0:
                    stalemate = False

            if stalemate:
                for car in self.active_cars:
                    car.change_speed(self, stalemate = True)

        for car in self.active_cars:
            car.do_small_step()

        new_active_cars = []
        for car in self.active_cars:
            if car.pos == car.target_pos:
                if car.returning:
                    # A car has finished
                    self.num_finished += 1
                    continue

                # A car has reached its target!
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

        if crash:
            raise CarCrashException("A crash has occured")
        
    # Should this really be here?
    def do_step_decisions(self):
        # Here all the decisions will be done
        pass

    def print_debug(self):
        print([car.pos for car in self.active_cars])
