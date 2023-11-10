import pygame as pg

WIN_WIDTH = 1920 # in pixel
WIN_HEIGHT = 1000 # in pixel
WIN_CLEAR_COLOR = (0, 0, 0) # (r, g, b), channell int [0, 255]

AREA_MARGIN = 50 # in pixel
AREA_RECT = (AREA_MARGIN, AREA_MARGIN, WIN_WIDTH - (AREA_MARGIN * 2), WIN_HEIGHT - (AREA_MARGIN * 2))
AREA_COLOR = (100, 100, 100) # (r, g, b), channell int [0, 255]
AREA_BORDER_SIZE = 10 # in pixel

BALL_RADIUS = 10 # in pixel
BALL_COLOR = (255, 255, 255) # (r, g, b), channell int [0, 255]
BALL_TRAIL_OPACITY = 0.5 # float [0, 1]
BALL_TRAIL_LENGTH = 30 # number of cicles in trail
BALL_START_SPEED = WIN_WIDTH / 4 # pixel per seconds
BALL_MIN_SPEED = WIN_WIDTH / 8 # pixel per seconds
BALL_MAX_SPEED = WIN_WIDTH * 2 # pixel per seconds
BALL_PADDLE_ACCELERATION = 100 # pixel per seconds
BALL_WALL_ACCELERATION = 10 # pixel per seconds
BALL_HITBOX_PRECISION = 16 # nb number for make circle [4, 360]
BALL_MOVE_STEP = BALL_RADIUS / 2 # Number of pixel travel by ball between 2 collisions check

BALL_FRICTION = False # boolean
BALL_MINIMUM_FRICTION = 100 # pixel per seconds
BALL_FRICTION_STRENGTH = 0.2 # float [0, 1]

PERFECT_SHOOT_SIZE = BALL_RADIUS * 4 # in pixel

TEAM_MAX_PLAYER = 2
TEAM_WIN_SCORE = 11

PADDLE_WIDTH = 14 # in pixel
PADDLE_HEIGHT = WIN_HEIGHT / 7 # in pixel
PADDLE_SPEED = WIN_HEIGHT / 1.5 # pixel per seconds
PADDLE_COLOR = (200, 200, 200) # (r, g, b), channell int [0, 255]
PADDLE_LAUNCH_COOLDOWN = 0.2 # In second

DRAW_HITBOX = False # boolean
DRAW_HITBOX_NORMALS = False # boolean
HITBOX_BALL_COLOR = (255, 0, 0) # (r, g, b), channell int [0, 255]
HITBOX_WALL_COLOR = (0, 255, 0) # (r, g, b), channell int [0, 255]
HITBOX_PADDLE_COLOR = (0, 0, 255) # (r, g, b), channell int [0, 255]

# Ball state defines
STATE_RUN = 0
STATE_IN_GOAL_LEFT = 1
STATE_IN_GOAL_RIGHT = 2
STATE_IN_FOLLOW = 3

# Key defines
KEY_UP = 0
KEY_DOWN = 1
KEY_POWER_UP = 2
KEY_LAUNCH_BALL = 3

# Power up defines
POWER_UP_NONE = -1
POWER_UP_BALL_FAST = 0
POWER_UP_BALL_SLOW = 1
POWER_UP_BALL_BIG = 2
POWER_UP_BALL_LITTLE = 3
POWER_UP_BALL_NO_COLLISION = 4
POWER_UP_BALL_PHATOM = 5
POWER_UP_PADDLE_FAST = 6
POWER_UP_PADDLE_SLOW = 7
POWER_UP_PADDLE_BIG = 8
POWER_UP_PADDLE_LITTLE = 9

# LEFT PLAYERS
PLAYER_KEYS = [
	(pg.K_q, pg.K_a, pg.K_z, pg.K_SPACE), # L1 player
	(pg.K_w, pg.K_s, pg.K_x, pg.K_SPACE), # L2 player
	(pg.K_o, pg.K_k, pg.K_m, pg.K_SPACE), # R1 player
	(pg.K_i, pg.K_j, pg.K_n, pg.K_SPACE), # R2 player
]
