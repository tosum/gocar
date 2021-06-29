from enum import Enum
import pygame
import random
import time

from intersection import Intersection, CarCrashException
from graphics import Graphics
from direction import Direction, directions
from car import CarStatistic, profiles

if __name__ == "__main__":
    road_len = 5

    pygame.init()

    print("Computing...")
    intersection = Intersection(road_len)

    for _ in range(8):
        dir_from = random.choice(directions)
        dir_to = random.choice(directions)

        while dir_from == dir_to:
            dir_to = random.choice(directions)

        points = random.randint(5, 15)

        profile = random.choice(profiles)

        intersection.add_car(dir_from, 0, dir_to, 1, profile, points)

    states = [intersection.copy()]
    stats = []
    while intersection.num_finished != intersection.num_cars or len(states) % 4 != 0:
        try:
            intersection.do_small_step()
        except CarCrashException:
            print("A crash has occured!")

        states.append(intersection.copy())

    for state in states:
        for car in state.active_cars:
                stats.append(CarStatistic(car))

    print("DONE")

    graphics = Graphics(road_len, 800, 800)

    running = True

    playing = True
    accumulated_time = 0
    state_time = 0.1
    cur_state = 0
    play_speed = 1.0

    start_time = time.time()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_RIGHT:
                    cur_state = cur_state + 1
                    if cur_state == len(states):
                        cur_state = 0

                if event.key == pygame.K_LEFT:
                    cur_state = cur_state - 1
                    if cur_state < 0:
                        cur_state = len(states) - 1

                if event.key == pygame.K_SPACE:
                    if playing:
                        playing = False
                    else:
                        playing = True
                        accumulated_time = False

                if event.key == pygame.K_UP:
                    play_speed += 0.1

                if event.key == pygame.K_DOWN:
                    play_speed -= 0.1
                    if play_speed < 0.1:
                        play_speed = 0.1
            
        cur_time = time.time()
        delta_t = cur_time - start_time
        start_time = cur_time

        if playing:
            accumulated_time += delta_t * play_speed

            while accumulated_time > state_time:
                cur_state = cur_state + 1
                if cur_state == len(states):
                    cur_state = 0

                accumulated_time -= state_time
        
        state_info = "{:.2f} / {}".format(cur_state / 4, len(states) // 4)
        speed_info = "Speed: {:.1f}".format(play_speed)
        
        graphics.draw(states[cur_state], state_info, speed_info)