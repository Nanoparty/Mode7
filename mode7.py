import pygame as pg
import numpy as np
from settings import *
from numba import njit, prange

class Mode7:
    def __init__(self, app):
        self.app = app
        self.floor_tex = pg.image.load('floor_2.png').convert()
        self.floor_tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)

        self.ceil_tex = pg.image.load('ceil_1.png').convert()
        self.ceil_tex_size = self.ceil_tex.get_size()
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.ceil_tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)

        self.screen_array = pg.surfarray.array3d(pg.Surface(WIN_RES))

        self.angle = 0.0
        self.pos = np.array([0.0, 0.0])

    def update(self):
        #time = self.app.time
        #pos = np.array([time, 0])
        #angle = np.sin(time * 0.3)
        self.movement();
        self.screen_array = self.render_frame(self.floor_array, self.ceil_array, self.screen_array, self.floor_tex_size, self.ceil_tex_size, self.pos, self.angle)

    @staticmethod
    @njit(fastmath=True, parallel=True)
    def render_frame(floor_array, ceil_array, screen_array, floor_tex_size, ceil_tex_size, pos, angle):

        sin, cos = np.sin(angle), np.cos(angle)

        # iterating over the screen array
        for i in prange(WIDTH):
            for j in range(HALF_HEIGHT, HEIGHT):
                # x y z
                x = HALF_WIDTH - i
                y = j + FOCAL_LEN
                z = j - HALF_HEIGHT + 1

                # angle
                rx = (x * cos - y * sin)
                ry = (x * sin + y * cos)

                # projection
                px = (rx / z + pos[1]) * SCALE
                py = (ry / z + pos[0]) * SCALE

                # floor pixel pos and color
                floor_pos = int(px % floor_tex_size[0]), int(py % floor_tex_size[1])
                floor_col = floor_array[floor_pos]

                ceil_pos = int(px % ceil_tex_size[0]), int(py % ceil_tex_size[1])
                ceil_col = ceil_array[ceil_pos]

                # shading
                attenuation = min(max(7.5 * (abs(z) / HALF_HEIGHT), 0), 1)
                fog = (1 - attenuation) * 10

                floor_col = (floor_col[0] * attenuation + fog,
                             floor_col[1] * attenuation + fog,
                             floor_col[2] * attenuation + fog)
                
                ceil_col = (ceil_col[0] * attenuation + fog,
                             ceil_col[1] * attenuation + fog,
                             ceil_col[2] * attenuation + fog)

                # fill screen array
                screen_array[i, j] = floor_col
                screen_array[i, -j] = ceil_col

        return screen_array

    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    def movement(self):
        sin_a = np.sin(self.angle)
        cos_a = np.cos(self.angle)
        dx, dy = 0, 0
        speed_sin = SPEED * sin_a
        speed_cos = SPEED * cos_a

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            dx += speed_cos
            dy += -speed_sin
        if keys[pg.K_s]:
            dx += -speed_cos
            dy += speed_sin
        if keys[pg.K_d]:
            dx += -speed_sin
            dy += -speed_cos
        if keys[pg.K_a]:
            dx += speed_sin
            dy += speed_cos
        self.pos[0] += dx
        self.pos[1] += dy

        if keys[pg.K_LEFT]:
            self.angle -= SPEED
        if keys[pg.K_RIGHT]:
            self.angle += SPEED

        
