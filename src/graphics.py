from enum import Enum
import pygame
from pygame import Vector2

from direction import Direction

class Input(Enum):
    Exit = 0

def inverse_color(c):
    return (255 - c[0], 255 - c[1], 255 - c[2])

def vec_add(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def vec_sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def vec_scalarmul(v, s):
    return (v[0] * s, v[1] * s)

class Graphics:
    def __init__(self, road_len, width, height):
        self.road_len = road_len
        self.width = width
        self.height = height

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))

        self.lines = self.generate_lines()
        self.polygon = self.generate_polygon()

        self.car_size = self.get_car_size()
        self.car_speed_font = pygame.font.SysFont(None, int(self.car_size * 0.8))
        self.info_font = pygame.font.SysFont(None, int(self.car_size * 0.6))

    def generate_lines(self):
        small = 0
        mid1 = small + 4 * self.road_len
        mid2 = mid1 + 4
        big = mid2 + 4 * self.road_len

        def square_lines(x, y):
            return [(x - 2, y - 2), (x - 2, y + 2), (x + 2, y + 2), (x + 2, y - 2), (x - 2, y - 2)]
        
        line_points = []

        for x in range(small, big+1, 4):
            line_points.extend(square_lines(x, mid1))
        
        for x in range(big, small-1, -4):
            line_points.extend(square_lines(x, mid2))

        line_points.extend(square_lines(mid1, mid2))

        for y in range(small, big+1, 4):
            line_points.extend(square_lines(mid1, y))

        for y in range(big, small-1, -4):
            line_points.extend(square_lines(mid2, y))

        return [self.inter_to_screen(p) for p in line_points]

    def generate_polygon(self):
        # Grey road background
        small = -2
        mid1 = small + 4 * self.road_len
        mid2 = mid1 + 8
        big = mid2 + 4 * self.road_len
        points = [(mid1, mid1), (mid1, small), (mid2, small), (mid2, mid1), (big, mid1), (big, mid2), (mid2, mid2), (mid2, big), (mid1, big), (mid1, mid2), (small, mid2), (small, mid1)]

        return [self.inter_to_screen(p) for p in points]

    def get_car_size(self):
        pos1 = self.inter_to_screen((0, 0))
        pos2 = self.inter_to_screen((4, 0))

        return 0.8 * abs(pos1[0] - pos2[0])

    def draw_car_speed(self, car):
        img = self.car_speed_font.render(str(car.speed), True, inverse_color(car.color))
        pos = self.inter_to_screen(car.pos)
        x = pos[0] - img.get_size()[0] / 2
        y = pos[1] - img.get_size()[1] / 2

        self.screen.blit(img, (x, y))

    def draw(self, intersection, state_info, speed_info):
        self.screen.fill((80, 130, 130))
        pygame.draw.polygon(self.screen, (240, 240, 240), self.polygon)
        pygame.draw.lines(self.screen, (0, 0, 0), False, self.lines, width = 2)

        for car in intersection.active_cars:
            # Draw car square
            pos = Vector2(self.inter_to_screen(car.pos))
            x = pos[0] - self.car_size / 2
            y = pos[1] - self.car_size / 2
            pygame.draw.rect(self.screen, car.color, (x + 2, y + 2, self.car_size, self.car_size))

            # Draw direction arrow
            sharpness = 0.29
            length = 1.1

            next_pos = Vector2(self.inter_to_screen(car.next_pos()))

            dir_vec = 1.3 * (next_pos - pos)
            orto_vec = Vector2(-dir_vec[1], dir_vec[0])
            
            arm1 = sharpness * (3 * dir_vec + orto_vec) - dir_vec
            arm2 = sharpness * (3 * dir_vec - orto_vec) - dir_vec

            top = pos + dir_vec
            arr1 = top + arm1 * length
            arr2 = top + arm2 * length

            pygame.draw.lines(self.screen, inverse_color(car.color), False, [arr1, top, arr2], width = 5)

            # Draw car speed
            self.draw_car_speed(car)

        state_info_img = self.info_font.render(state_info, True, (255, 255, 255))
        speed_info_img = self.info_font.render(speed_info, True, (255, 255, 255))
        self.screen.blit(state_info_img, (20, 20))
        self.screen.blit(speed_info_img, (20, 20 + state_info_img.get_size()[1] + 20))

        pygame.display.flip()

    # Convert intersection coordinates to screen coordinates
    def inter_to_screen(self, pos):
        size = min(self.width, self.height)
        margin = 20

        x_begin = self.width // 2 - size // 2 + margin
        y_begin = self.height // 2 - size // 2 + margin

        x_end = x_begin + size - 2 * margin
        y_end = y_begin + size - 2 * margin

        # -2 maps to begin
        # 4 * (2 * road_len + 1) + 2 maps to end

        x = x_begin + (pos[0] - (-2)) / (4 * (2 * self.road_len + 1) + 2 - (-2)) * (x_end - x_begin)
        y = y_begin + (pos[1] - (-2)) / (4 * (2 * self.road_len + 1) + 2 - (-2)) * (y_end - y_begin)

        return (x, y)

    def handle_input(self):
        pass