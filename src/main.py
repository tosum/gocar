
from intersection import Intersection
from direction import Direction, directions
from car import CarStatistic, Profile, profiles
import random

def letter_to_dir(letter):
    if letter == 'N':
        return Direction.Up
    elif letter == 'E':
        return Direction.Right
    elif letter == 'S':
        return Direction.Down
    elif letter == 'W':
        return Direction.Left
    
def letter_to_profile(letter):
    if letter == 'R':
        return Profile.Righteous
    elif letter == 'H':
        return Profile.Hoarder
    elif letter == 'N':
        return Profile.Nervous
    elif letter == 'F':
        return Profile.Frustrated
    elif letter == 'A':
        return Profile.Altruistic

def read_cars(cars_num):
    cars = []
    for _ in range(cars_num):
        elems = input().split(' ')

        ts = int(elems[0])
        start_dir = letter_to_dir(elems[1])
        t1 = int(elems[2])
        target_dir = letter_to_dir(elems[3])
        target_rest = int(elems[4])
        profile = letter_to_profile(elems[5])
        points = int(elems[6])

        start_rest = ts + t1

        if start_dir == target_dir:
            print("BAD CAR - start dir equals target dir")
            continue

        cars.append((start_dir, start_rest, target_dir, target_rest, profile, points))
    
    print(f"Read {len(cars)} cars from the input")
    return cars

def is_right_turn(dir1, dir2):
    if dir1 == Direction.Up and dir2 == Direction.Left:
        return True

    if dir1 == Direction.Right and dir2 == Direction.Up:
        return True

    if dir1 == Direction.Down and dir2 == Direction.Right:
        return True

    if dir1 == Direction.Left and dir2 == Direction.Down:
        return True

    return False

def is_left_turn(dir1, dir2):
    if dir1 == Direction.Up and dir2 == Direction.Right:
        return True

    if dir1 == Direction.Right and dir2 == Direction.Down:
        return True

    if dir1 == Direction.Down and dir2 == Direction.Left:
        return True

    if dir1 == Direction.Left and dir2 == Direction.Up:
        return True

    return False

def print_stats(stats, intersection_time_stats):
    speeds = [stat.speed for stat in stats]
    avg_speed = sum(speeds)
    if len(speeds) > 0:
        avg_speed /= len(speeds)

    times = [stat[1] for stat in intersection_time_stats]
    avg_time = sum(times)
    if len(times) > 0:
        avg_time /= len(times)

    print(f"Average speed: {avg_speed:.2f}")
    print(f"Average time spent on the intersection: {avg_time:.2f}")

def get_car_stat(stat):
    try:
        a = stat.speed
        return stat
    except:
        return stat[0]

def filter_turn(stat_in, turn):
    stat = get_car_stat(stat_in)
    if turn == 'all':
        return True
    if turn == 'left' and is_left_turn(stat.from_dir, stat.to_dir):
        return True
    if turn == 'right' and is_right_turn(stat.from_dir, stat.to_dir):
        return True

    return False

def filter_profile(stat_in, profile):
    stat = get_car_stat(stat_in)
    if profile == 'all':
        return True

    return profile == stat.profile

def filter_haste(stat_in, haste):
    stat = get_car_stat(stat_in)
    if haste == 'any':
        return True

    return haste == stat.haste

def print_many_stats(stats, time_stats):
    print("\nAll cases:")
    print_stats(stats, time_stats)

    for turn in ['all', 'left', 'right']:
        new_stats = list(filter(lambda s : filter_turn(s, turn), stats))
        new_time_stats = list(filter(lambda s : filter_turn(s, turn), time_stats))

        profs = [
            'all',
            Profile.Righteous,
            Profile.Hoarder,
            Profile.Nervous,
            Profile.Frustrated,
            Profile.Altruistic
        ]

        for profile in profs:
            print("\nTurn:", turn)
            print("Profile:", str(profile))
            stats2 = list(filter(lambda s : filter_profile(s, profile), new_stats))
            time_stats2 = list(filter(lambda s : filter_profile(s, profile), new_time_stats))
            print_stats(stats2, time_stats2)

        for haste in ['any', 0, 1, 2, 3, 4, 5]:
            print("\nTurn:", turn)
            print("Haste: ", haste)
            stats2 = list(filter(lambda s : filter_haste(s, haste), new_stats))
            time_stats2 = list(filter(lambda s : filter_haste(s, haste), new_time_stats))
            print_stats(stats2, time_stats2)
        
    print("\n")

if __name__ == "__main__":
    params = input().split(' ')

    road_len = int(params[0])
    cars_num = int(params[1])
    simulation_steps = int(params[2])
    
    print("road length:", road_len)
    print("number of cars:", cars_num)
    print("simulation steps:", simulation_steps)

    visualisation = True
    cars = read_cars(cars_num)

    intersection = Intersection(road_len)

    for (start_dir, start_rest, target_dir, target_rest, profile, points) in cars:
        intersection.add_car(start_dir, start_rest, target_dir,target_rest, profile, points)

    random.seed(406120)
    print("Computing...")
    
    states = [intersection.copy()]
    stats = []
    intersection_time_stats = []
    while intersection.num_finished != intersection.num_cars or len(states) % 4 != 0:        
        crashed = intersection.do_small_step(intersection_time_stats)

        if len(crashed) > 0:
            print("Crash! Car ids: ", crashed)

        if intersection.time % 4 == 0:
            print(f"Step {intersection.time // 4}...")

        states.append(intersection.copy())

        if intersection.time / 4 > simulation_steps:
            break

    for state in states:
        for car in state.active_cars:
            stats.append(CarStatistic(car))

    print("DONE")

    print_many_stats(stats, intersection_time_stats)

    if visualisation:
        print("\nStarting visualisation!\n")
        from graphics import Graphics
        graphics = Graphics(road_len, 800, 800)
        graphics.run(states)