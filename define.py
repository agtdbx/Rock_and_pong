import pygame as pg

WIN_WIDTH = 1280 # in pixel
WIN_HEIGHT = 700 # in pixel
WIN_CLEAR_COLOR = (0, 0, 0) # (r, g, b), channell int [0, 255]

AREA_MARGIN = 50 # in pixel
AREA_RECT = (AREA_MARGIN, AREA_MARGIN, WIN_WIDTH - (AREA_MARGIN * 2), WIN_HEIGHT - (AREA_MARGIN * 2))
AREA_COLOR = (100, 100, 100) # (r, g, b), channell int [0, 255]
AREA_BORDER_SIZE = 10 # in pixel

BALL_RADIUS = 10 # in pixel
BALL_COLOR = (255, 255, 255) # (r, g, b), channell int [0, 255]
BALL_TRAIL_OPACITY = 0.5 # float [0, 1]
BALL_TRAIL_LENGTH = 30 # number of cicles in trail
BALL_START_SPEED = 200 # pixel per seconds
BALL_MAX_SPEED = 2000 # pixel per seconds
BALL_ACCELERATION = 0.1 # float [0, 1]
BALL_HITBOX_PRECISION = 16 # nb number for make circle [4, 360]

BALL_FRICTION = False # boolean
BALL_MINIMUM_FRICTION = 100 # pixel per seconds
BALL_FRICTION_STRENGTH = 0.2 # float [0, 1]

PERFECT_SHOOT_SIZE = BALL_RADIUS * 4 # in pixel

PADDLE_WIDTH = 14 # in pixel
PADDLE_HEIGHT = 100 # in pixel
PADDLE_SPEED = 300 # pixel per seconds
PADDLE_COLOR = (200, 200, 200) # (r, g, b), channell int [0, 255]

PLAYER_1_UP = pg.K_q
PLAYER_1_DOWN = pg.K_a
PLAYER_1_POWERUP = pg.K_z
PLAYER_1_LAUNCH_BALL = pg.K_SPACE

PLAYER_2_UP = pg.K_e
PLAYER_2_DOWN = pg.K_d
PLAYER_2_POWERUP = pg.K_c
PLAYER_2_LAUNCH_BALL = pg.K_SPACE

DRAW_HITBOX = False # boolean
DRAW_HITBOX_NORMALS = False # boolean
HITBOX_BALL_COLOR = (255, 0, 0) # (r, g, b), channell int [0, 255]
HITBOX_WALL_COLOR = (0, 255, 0) # (r, g, b), channell int [0, 255]
HITBOX_PADDLE_COLOR = (0, 0, 255) # (r, g, b), channell int [0, 255]

STATE_RUN = 0
STATE_IN_GOAL_LEFT = 1
STATE_IN_GOAL_RIGHT = 2
STATE_IN_FOLLOW_LEFT = 10
STATE_IN_FOLLOW_RIGHT = 20
