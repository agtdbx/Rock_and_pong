import pygame as pg

############################################################################################
#                                      WINDOW DEFINE                                       #
############################################################################################
WIN_WIDTH = 1920 # in pixel
WIN_HEIGHT = 1000 # in pixel
WIN_CLEAR_COLOR = (0, 0, 0) # (r, g, b), channell int [0, 255]


############################################################################################
#                                      BALL DEFINE                                       #
############################################################################################
BALL_RADIUS = 10 # in pixel
BALL_COLOR = (255, 255, 255) # (r, g, b), channell int [0, 255]
BALL_TRAIL_OPACITY = 0.5 # float [0, 1]
BALL_TRAIL_LENGTH = 30 # number of cicles in trail
BALL_START_SPEED = WIN_WIDTH // 4 # pixel per seconds
BALL_MIN_SPEED = WIN_WIDTH // 8 # pixel per seconds
BALL_MAX_SPEED = WIN_WIDTH * 2 # pixel per seconds
BALL_PADDLE_ACCELERATION = 100 # pixel per seconds
BALL_WALL_ACCELERATION = 10 # pixel per seconds
BALL_HITBOX_PRECISION = 16 # nb number for make circle [4, 360]
BALL_MOVE_STEP = 2 # Number of pixel travel by ball between 2 collisions check

BALL_FRICTION = False # boolean
BALL_MINIMUM_FRICTION = 100 # pixel per seconds
BALL_FRICTION_STRENGTH = 0.2 # float [0, 1]

# Ball state defines
STATE_RUN = 0
STATE_IN_GOAL_LEFT = 1
STATE_IN_GOAL_RIGHT = 2
STATE_IN_FOLLOW = 3


############################################################################################
#                                        MAP DEFINE                                        #
############################################################################################
AREA_MARGIN = 50 # in pixel
AREA_RECT = (AREA_MARGIN, AREA_MARGIN, WIN_WIDTH - (AREA_MARGIN * 2), WIN_HEIGHT - (AREA_MARGIN * 2))
AREA_COLOR = (100, 100, 100) # (r, g, b), channell int [0, 255]
AREA_BORDER_SIZE = 10 # in pixel
SPACE_PART = AREA_RECT[2] // 5
LEFT_TEAM_RECT = (AREA_RECT[0], AREA_RECT[1], SPACE_PART, AREA_RECT[3])
LEFT_TEAM_COLOR = (100, 100, 150) # (r, g, b), channell int [0, 255]
MIDDLE_RECT = (AREA_RECT[0] + SPACE_PART, AREA_RECT[1], AREA_RECT[2] - SPACE_PART, AREA_RECT[3])
MIDDLE_COLOR = (100, 100, 100) # (r, g, b), channell int [0, 255]
RIGTH_TEAM_RECT = (AREA_RECT[0] + AREA_RECT[2] - SPACE_PART, AREA_RECT[1], SPACE_PART, AREA_RECT[3])
RIGTH_TEAM_COLOR = (150, 100, 100) # (r, g, b), channell int [0, 255]

PERFECT_SHOOT_SIZE = BALL_RADIUS * 4 # in pixel


############################################################################################
#                                        TEAM DEFINE                                       #
############################################################################################
TEAM_MAX_PLAYER = 2
TEAM_WIN_SCORE = 11

############################################################################################
#                                       PADDLE DEFINE                                      #
############################################################################################
PADDLE_WIDTH = 14 # in pixel
PADDLE_HEIGHT = WIN_HEIGHT / 7 # in pixel
PADDLE_SPEED = WIN_HEIGHT / 1.5 # pixel per seconds
PADDLE_COLOR = (200, 200, 200) # (r, g, b), channell int [0, 255]
PADDLE_LAUNCH_COOLDOWN = 0.2 # In second


############################################################################################
#                                       DEBUG DEFINE                                       #
############################################################################################
DRAW_HITBOX = False # boolean
DRAW_HITBOX_NORMALS = False # boolean
HITBOX_BALL_COLOR = (255, 0, 0) # (r, g, b), channell int [0, 255]
HITBOX_WALL_COLOR = (0, 255, 0) # (r, g, b), channell int [0, 255]
HITBOX_PADDLE_COLOR = (0, 0, 255) # (r, g, b), channell int [0, 255]


############################################################################################
#                                       POWER UP DEFINE                                    #
############################################################################################
POWER_UP_ENABLE = True
# Power up object state
POWER_UP_HITBOX_RADIUS = 16 # in pixel
POWER_UP_HITBOX_PRECISION = 8 # number of point to make the circle hitbox
POWER_UP_HITBOX_COLOR = (200, 100, 100) # (r, g, b), channell int [0, 255]
POWER_UP_VISIBLE = 0
POWER_UP_TAKE = -1
POWER_UP_SPAWN_COOLDOWN = 5 # in seconds
POWER_UP_USE_COOLDOWN = 0.5 # in seconds

# Power up list and effects define
POWER_UP_NONE = -1

POWER_UP_BALL_FAST = 0 # begin by hit paddle - 1 ball - end by hit wall
POWER_UP_BALL_FAST_FACTOR = 2.5 # multiply the speed
POWER_UP_BALL_FAST_TIME_STOP = 1 # in seconds
POWER_UP_BALL_FAST_COLOR = (200, 0, 200) # in seconds

POWER_UP_BALL_WAVE = 1 # begin by hit paddle - 1 ball - end by hit wall
POWER_UP_BALL_WAVE_DEGREES = 45 # in degrees [0, 359]
POWER_UP_BALL_WAVE_SPEED_FACTOR = 20 # change the frequence of the wave. High = more but smaller waves
POWER_UP_BALL_WAVE_COLOR = (0, 200, 200) # in seconds

POWER_UP_BALL_INVISIBLE = 2 # begin by hit paddle - 1 ball - end by hit wall
POWER_UP_BALL_INVISIBLE_SPEED_FACTOR = 5 # in seconds
POWER_UP_BALL_INVISIBLE_COLOR = (200, 200, 0) # in seconds

POWER_UP_BALL_NO_COLLISION = 3 # begin when ball isn't close of ennemy - all ball - end by hit paddle

POWER_UP_DUPLICATION_BALL = 4 # begin when ball isn't close of ennemy - all ball - never end
POWER_UP_DUPLICATION_BALL_SPEED_REDUCE_FACTOR = 2 # divise the speed
POWER_UP_DUPLICATION_BALL_DEGREES_DEVIATON = 30

POWER_UP_BALL_SLOW = 5 # any time - all ball - limited time effect
POWER_UP_BALL_SLOW_SPEED_FACTOR = 2 # divide the speed
POWER_UP_BALL_SLOW_TIME_EFFECT = 5 # in seconds

POWER_UP_BALL_STOP = 6 # any time - all ball - limited time effect
POWER_UP_BALL_STOP_TIMER_EFFECT = 5 # in seconds

POWER_UP_BALL_BIG = 7 # any time - all ball - limited time effect
POWER_UP_BALL_BIG_SIZE_FACTOR = 2 # multiply the size
POWER_UP_BALL_BIG_TIME_EFFECT = 5 # in seconds

POWER_UP_BALL_LITTLE = 8 # any time - all ball - limited time effect
POWER_UP_BALL_LITTLE_SIZE_FACTOR = 2 # divide the size
POWER_UP_BALL_LITTLE_TIME_EFFECT = 5 # in seconds

POWER_UP_PADDLE_FAST = 9 # any time - all team paddle - limited time effect
POWER_UP_PADDLE_FAST_SPEED_FACTOR = 2 # multiply the speed
POWER_UP_PADDLE_FAST_TIME_EFFECT = 5 # in seconds

POWER_UP_PADDLE_SLOW = 10 # any time - all ennemy team paddle - limited time effect
POWER_UP_PADDLE_SLOW_SPEED_FACTOR = 2 # divide the speed
POWER_UP_PADDLE_SLOW_TIME_EFFECT = 5 # in seconds

POWER_UP_PADDLE_BIG = 11 # any time - all team paddle - limited time effect
POWER_UP_PADDLE_BIG_SIZE_FACTOR = 2 # multiply the size
POWER_UP_PADDLE_BIG_TIME_EFFECT = 5 # in seconds

POWER_UP_PADDLE_LITTLE = 12 # any time - all ennemy team paddle - limited time effect
POWER_UP_PADDLE_LITTLE_SIZE_FACTOR = 2 # divide the size
POWER_UP_PADDLE_LITTLE_TIME_EFFECT = 5 # in seconds


############################################################################################
#                                      CLIENT DEFINE                                       #
############################################################################################
# Key index defines
KEY_UP = 0
KEY_DOWN = 1
KEY_POWER_UP = 2
KEY_LAUNCH_BALL = 3

## PLAYERS KEYS QWERTY
#PLAYER_KEYS = [
#	(pg.K_q, pg.K_a, pg.K_z, pg.K_SPACE), # L1 player
#	(pg.K_w, pg.K_s, pg.K_x, pg.K_SPACE), # L2 player
#	(pg.K_o, pg.K_k, pg.K_m, pg.K_SPACE), # R1 player
#	(pg.K_i, pg.K_j, pg.K_n, pg.K_SPACE), # R2 player
#]

# PLAYERS KEYS AZERTY
PLAYER_KEYS = [
(pg.K_a, pg.K_q, pg.K_w, pg.K_SPACE), # L1 player
(pg.K_z, pg.K_s, pg.K_x, pg.K_SPACE), # L2 player
(pg.K_o, pg.K_k, pg.K_COMMA, pg.K_SPACE), # R1 player
(pg.K_i, pg.K_j, pg.K_n, pg.K_SPACE), # R2 player
]
