from define import *
from pg_utils import *
from vec2 import *
import hitbox
import paddle
import ball

import pygame as pg
import math
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
			paddle.Paddle(AREA_RECT[0] + AREA_BORDER_SIZE * 2, WIN_HEIGHT / 2, 1),
			paddle.Paddle(AREA_RECT[0] + AREA_RECT[2] - AREA_BORDER_SIZE * 2, WIN_HEIGHT / 2, 2)
		]

		# Ball creation
		self.balls = [ball.Ball(WIN_WIDTH / 2, WIN_HEIGHT / 2)]

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
				[(-100, 0), (100, 0), (50, 75), (0, 100), (-50, 75)],
				(150, 150, 0)
			),
			createObstacle(
				AREA_RECT[0] + AREA_RECT[2] / 2,
				AREA_RECT[1] + AREA_RECT[3],
				[(-100, 0), (100, 0), (50, -75), (0, -100), (-50, -75)],
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

		for p in self.paddles:
			if p.waitLaunch > 0:
				p.waitLaunch -= delta
				if p.waitLaunch < 0:
					p.waitLaunch = 0

		if self.keyboardState[PLAYER_1_UP]:
			self.paddles[0].move("up", delta)
		if self.keyboardState[PLAYER_1_DOWN]:
			self.paddles[0].move("down", delta)

		if self.keyboardState[PLAYER_2_UP]:
			self.paddles[1].move("up", delta)
		if self.keyboardState[PLAYER_2_DOWN]:
			self.paddles[1].move("down", delta)

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
				b.state = STATE_IN_FOLLOW_LEFT

			# if the ball is in right goal
			elif b.state == STATE_IN_GOAL_RIGHT:
				self.player1Score += 1
				b.direction = Vec2(-1, 0)
				b.speed = BALL_START_SPEED
				b.state = STATE_IN_FOLLOW_RIGHT

			# if the ball must follow the left paddle
			elif b.state == STATE_IN_FOLLOW_LEFT:
				b.setPos(vec2Add(self.paddles[0].pos, Vec2(PADDLE_WIDTH * 2, 0)))
				if self.keyboardState[PLAYER_1_LAUNCH_BALL] and self.paddles[0].waitLaunch == 0:
					b.state = STATE_RUN
					self.paddles[0].waitLaunch = 0.5

			# if the ball must follow the right paddle
			elif b.state == STATE_IN_FOLLOW_RIGHT:
				b.setPos(vec2Add(self.paddles[1].pos, Vec2(-PADDLE_WIDTH * 2, 0)))
				if self.keyboardState[PLAYER_2_LAUNCH_BALL] and self.paddles[1].waitLaunch == 0:
					b.state = STATE_RUN
					self.paddles[1].waitLaunch = 0.5

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
