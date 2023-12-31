import pygame as pg

from define import *

############################################################################################
#                                      WINDOW DEFINE                                       #
############################################################################################
WIN_WIDTH = 1920 # in pixel
WIN_HEIGHT = 1000 # in pixel
WIN_CLEAR_COLOR = (0, 0, 0) # (r, g, b), channel int [0, 255]


############################################################################################
#                                      BALL DEFINE                                       #
############################################################################################
BALL_COLOR = (255, 255, 255) # (r, g, b), channel int [0, 255]
BALL_TRAIL_OPACITY = 0.5 # float [0, 1]
BALL_TRAIL_LENGTH = 30 # number of cicles in trail


############################################################################################
#                                        MAP DEFINE                                        #
############################################################################################
AREA_RECT = ((WIN_WIDTH - AREA_SIZE[0]) // 2, (WIN_HEIGHT - AREA_SIZE[1]) // 2, AREA_SIZE[0], AREA_SIZE[1])
AREA_COLOR = (100, 100, 100) # (r, g, b), channel int [0, 255]

AREA_LEFT_TEAM_RECT = (AREA_RECT[0], AREA_RECT[1], SPACE_PART, AREA_SIZE[1])
AREA_MIDDLE_RECT = (AREA_RECT[0] + SPACE_PART, AREA_RECT[1], AREA_SIZE[0] - SPACE_PART, AREA_SIZE[1])
AREA_RIGTH_TEAM_RECT = (AREA_RECT[0] + AREA_SIZE[0] - SPACE_PART, AREA_RECT[1], SPACE_PART, AREA_SIZE[1])
AREA_TEAM_COLOR = (90, 90, 90) # (r, g, b), channel int [0, 255]


############################################################################################
#                                       PADDLE DEFINE                                      #
############################################################################################
PADDLE_COLOR = (200, 200, 200) # (r, g, b), channell int [0, 255]


############################################################################################
#                                       DEBUG DEFINE                                       #
############################################################################################
DRAW_HITBOX = False # boolean
DRAW_HITBOX_NORMALS = False # boolean
HITBOX_BALL_COLOR = (255, 0, 0) # (r, g, b), channel int [0, 255]
HITBOX_WALL_COLOR = (0, 255, 0) # (r, g, b), channel int [0, 255]
HITBOX_PADDLE_COLOR = (0, 0, 255) # (r, g, b), channel int [0, 255]


############################################################################################
#                                       POWER UP DEFINE                                    #
############################################################################################
# Power up object state
POWER_UP_HITBOX_COLOR = (200, 100, 100) # (r, g, b), channell int [0, 255]

# Power up list and effects define
POWER_UP_BALL_FAST_COLOR = (200, 0, 200) # in seconds
POWER_UP_BALL_WAVE_COLOR = (0, 200, 200) # in seconds
POWER_UP_BALL_INVISIBLE_COLOR = (200, 200, 0) # in seconds


############################################################################################
#                                      CLIENT DEFINE                                       #
############################################################################################
# PLAYERS KEYS QWERTY
PLAYER_KEYS = [
	(pg.K_q, pg.K_a, pg.K_z, pg.K_SPACE), # L1 player
	(pg.K_w, pg.K_s, pg.K_x, pg.K_SPACE), # L2 player
	(pg.K_o, pg.K_k, pg.K_m, pg.K_SPACE), # R1 player
	(pg.K_i, pg.K_j, pg.K_n, pg.K_SPACE), # R2 player
]

# # PLAYERS KEYS AZERTY
# PLAYER_KEYS = [
# (pg.K_a, pg.K_q, pg.K_w, pg.K_SPACE), # L1 player
# (pg.K_z, pg.K_s, pg.K_x, pg.K_SPACE), # L2 player
# (pg.K_o, pg.K_k, pg.K_COMMA, pg.K_SPACE), # R1 player
# (pg.K_i, pg.K_j, pg.K_n, pg.K_SPACE), # R2 player
# ]
