from define import *
from pg_utils import *
from vec2 import *
import hitbox
import paddle
import ball

import pygame as pg
import random
import time
import sys


def createWall(x, y, w, h, color) -> hitbox.Hitbox:
	halfW = w / 2
	halfH = h / 2

	hit = hitbox.Hitbox(x, y, HITBOX_WALL_COLOR, color)
	hit.addPoint(-halfW, -halfH)
	hit.addPoint(halfW, -halfH)
	hit.addPoint(halfW, halfH)
	hit.addPoint(-halfW, halfH)

	return hit


def createObstacle(x:int, y:int, listPoint:list, color:tuple) -> hitbox.Hitbox:
	hit = hitbox.Hitbox(x, y, HITBOX_WALL_COLOR, color)

	for p in listPoint:
		hit.addPoint(p[0], p[1])

	return hit



class Game:
	def __init__(self):
		"""
		This method define all variables needed by the program
		"""
		# Start of pygame
		pg.init()

		# We remove the toolbar of the window's height
		self.winSize = ((WIN_WIDTH, WIN_HEIGHT))
		# We create the window
		self.win = pg.display.set_mode(self.winSize, pg.RESIZABLE)

		self.clock = pg.time.Clock() # The clock be used to limit our fps
		self.fps = 60

		self.last = time.time()

		self.runMainLoop = True

		self.inputWait = 0

		# Padd
		self.paddles = [
			# L1
			paddle.Paddle(AREA_RECT[0] + AREA_BORDER_SIZE * 2, WIN_HEIGHT / 2, 0),
			# R1
			paddle.Paddle(AREA_RECT[0] + AREA_RECT[2] - AREA_BORDER_SIZE * 2, WIN_HEIGHT / 2, 1),
			# # L2
			# paddle.Paddle(AREA_RECT[0] + AREA_BORDER_SIZE * 2, WIN_HEIGHT / 2 + PADDLE_WIDTH + 10, 2),
			# # R2
			# paddle.Paddle(AREA_RECT[0] + AREA_RECT[2] - AREA_BORDER_SIZE * 2, WIN_HEIGHT / 2 + PADDLE_WIDTH + 10, 3)
		]

		# Ball creation
		self.balls = [ball.Ball(WIN_WIDTH / 2, WIN_HEIGHT / 2)]

		self.balls[0].state = STATE_IN_FOLLOW
		self.balls[0].lastPaddleHitId = 0
		self.balls[0].direction = Vec2(1, 0)

		circlePointWall = []
		circlePointWallPrecision = 64
		circlePointWallRadius = 100

		for i in range(circlePointWallPrecision):
			degree = 360 / circlePointWallPrecision * i
			radian = degree * (math.pi / 180)
			x = circlePointWallRadius * math.cos(radian)
			y = circlePointWallRadius * math.sin(radian)
			circlePointWall.append((x, y))

		# Walls creation
		self.walls = [
			# Wall up
			createWall(
				AREA_RECT[0] + AREA_RECT[2] / 2,
			 	AREA_RECT[1] + AREA_BORDER_SIZE / 2,
				AREA_RECT[2],
				AREA_BORDER_SIZE,
				(50, 50, 50)
			),
			# Wall down
			createWall(
				AREA_RECT[0] + AREA_RECT[2] / 2,
				AREA_RECT[1] + AREA_RECT[3] - AREA_BORDER_SIZE / 2,
				AREA_RECT[2],
				AREA_BORDER_SIZE,
				(50, 50, 50)
			),
			# Obstables
			createObstacle(
				AREA_RECT[0] + AREA_RECT[2] / 2,
				AREA_RECT[1],
				[(-300, 0), (300, 0), (275, 50), (75, 75), (0, 125), (-75, 75), (-275, 50)],
				(150, 150, 0)
			),
			createObstacle(
				AREA_RECT[0] + AREA_RECT[2] / 2,
				AREA_RECT[1] + AREA_RECT[3],
				[(-300, 0), (300, 0), (275, -50), (0, -25), (-275, -50)],
				(150, 150, 0)
			),
			createObstacle(
				AREA_RECT[0] + AREA_RECT[2] / 2,
				AREA_RECT[1] + AREA_RECT[3] / 2,
				circlePointWall,
				(150, 150, 0)
			)
		]

		# Scores
		self.player1Score = 0
		self.player2Score = 0


	def run(self):
		"""
		This method is the main loop of the game
		"""
		# Game loop
		while self.runMainLoop:
			self.input()
			self.tick()
			self.render()
			self.clock.tick(self.fps)


	def input(self):
		"""
		The method catch user's inputs, as key presse or a mouse click
		"""
		# We check each event
		for event in pg.event.get():
			# If the event it a click on the top right cross, we quit the game
			if event.type == pg.QUIT:
				self.quit()

		self.keyboardState = pg.key.get_pressed()
		self.mouseState = pg.mouse.get_pressed()
		self.mousePos = pg.mouse.get_pos()

		# Press espace to quit
		if self.keyboardState[pg.K_ESCAPE]:
			self.quit()


	def tick(self):
		"""
		This is the method where all calculations will be done
		"""
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		if self.inputWait > 0:
			self.inputWait -= delta
			if self.inputWait < 0:
				self.inputWait = 0

		for i in range(len(self.paddles)):
			if self.paddles[i].waitLaunch > 0:
				self.paddles[i].waitLaunch -= delta
				if self.paddles[i].waitLaunch < 0:
					self.paddles[i].waitLaunch = 0

			if self.keyboardState[PLAYER_KEYS[i][KEY_UP]]:
				self.paddles[i].move("up", delta)
			if self.keyboardState[PLAYER_KEYS[i][KEY_DOWN]]:
				self.paddles[i].move("down", delta)

		newBalls = []

		for b in self.balls:
			b.updatePosition(delta, self.paddles, self.walls)

			if b.state == STATE_RUN and self.keyboardState[pg.K_v] and self.inputWait == 0:
				newBalls.append(b.dup())

			# if the ball is in left goal
			elif b.state == STATE_IN_GOAL_LEFT:
				self.player2Score += 1
				b.direction = Vec2(1, 0)
				b.speed = BALL_START_SPEED
				b.state = STATE_IN_FOLLOW
				b.lastPaddleHitId = self.paddles[0].id
				if len(self.paddles) == 4 and random.random() > 0.5:
					b.lastPaddleHitId = self.paddles[2].id

			# if the ball is in right goal
			elif b.state == STATE_IN_GOAL_RIGHT:
				self.player1Score += 1
				b.direction = Vec2(-1, 0)
				b.speed = BALL_START_SPEED
				b.state = STATE_IN_FOLLOW
				b.lastPaddleHitId = self.paddles[1].id
				if len(self.paddles) == 4 and random.random() > 0.5:
					b.lastPaddleHitId = self.paddles[3].id

			# case of ball follow player
			elif b.state == STATE_IN_FOLLOW:
				padId = b.lastPaddleHitId
				b.setPos(self.paddles[padId].pos.dup())
				b.pos.translateAlong(b.direction.dup(), PADDLE_WIDTH * 2)
				if self.keyboardState[PLAYER_KEYS[padId][KEY_LAUNCH_BALL]] and self.paddles[padId].waitLaunch == 0:
					b.state = STATE_RUN
					self.paddles[padId].waitLaunch = PADDLE_LAUNCH_COOLDOWN

		self.balls.extend(newBalls)

		if self.keyboardState[pg.K_v] and self.inputWait == 0:
			self.inputWait = 1

		pg.display.set_caption(str(self.clock.get_fps()))


	def render(self):
		"""
		This is the method where all graphic update will be done
		"""
		# We clean our screen with one color
		self.win.fill((0, 0, 0))

		# Draw area
		pg.draw.rect(self.win, AREA_COLOR, AREA_RECT)

		# Draw walls
		for w in self.walls:
			w.drawFill(self.win)

		# Draw ball
		for b in self.balls:
			b.draw(self.win)

		# Draw paddles
		for pad in self.paddles:
			pad.draw(self.win)

		# Draw score
		drawText(self.win, "Player 1 : " + str(self.player1Score), (AREA_MARGIN, AREA_MARGIN / 2), (255, 255, 255), size=30, align="mid-left")
		drawText(self.win, "Player 2 : " + str(self.player2Score), (WIN_WIDTH - AREA_MARGIN, AREA_MARGIN / 2), (255, 255, 255), size=30, align="mid-right")

		# We update the drawing.
		# Before the function call, any changes will be not visible
		pg.display.update()


	def quit(self):
		"""
		This is the quit method
		"""
		# Pygame quit
		pg.quit()
		sys.exit()


Game().run() # Start game
