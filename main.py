from define import *
from vec2 import *
import hitbox
import team
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

		# Team creation
		self.teamLeft = team.Team(1, leftSide=True)
		self.teamRight = team.Team(1, leftSide=False)

		# Ball creation
		self.balls = [ball.Ball(WIN_WIDTH / 2, WIN_HEIGHT / 2)]

		# Ball begin left side
		if random.random() > 0.5:
			self.balls[0].lastPaddleHitId = random.choice(self.teamLeft.paddles).id
		# Ball begin right side
		else:
			self.balls[0].lastPaddleHitId = random.choice(self.teamRight.paddles).id
			self.balls[0].direction = Vec2(-1, 0)

		# Walls creation
		circlePointWall = ball.getPointOfCircle(100, 32, 360 / 64)

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

		self.teamLeft.tick(delta, self.keyboardState, self.balls)
		self.teamRight.tick(delta, self.keyboardState, self.balls)

		newBalls = []

		for b in self.balls:
			b.updatePosition(delta, self.teamLeft.paddles, self.teamRight.paddles, self.walls)
			b.updateTime(delta)

			if b.state == STATE_RUN and self.keyboardState[pg.K_v] and self.inputWait == 0:
				newBalls.append(b.dup())

			# if the ball is in left goal
			elif b.state == STATE_IN_GOAL_LEFT:
				self.teamRight.score += 1
				b.direction = Vec2(1, 0)
				b.speed = BALL_START_SPEED
				b.state = STATE_IN_FOLLOW
				b.modifierSkipCollision = False
				b.lastPaddleHitId = random.choice(self.teamLeft.paddles).id

			# if the ball is in right goal
			elif b.state == STATE_IN_GOAL_RIGHT:
				self.teamLeft.score += 1
				b.direction = Vec2(-1, 0)
				b.speed = BALL_START_SPEED
				b.state = STATE_IN_FOLLOW
				b.modifierSkipCollision = False
				b.lastPaddleHitId = random.choice(self.teamRight.paddles).id

			# case of ball follow player
			elif b.state == STATE_IN_FOLLOW:
				if b.lastPaddleHitId < 2:
					pad = self.teamLeft.paddles[b.lastPaddleHitId]
				else:
					pad = self.teamRight.paddles[b.lastPaddleHitId - TEAM_MAX_PLAYER]
				b.setPos(pad.pos.dup())
				b.pos.translateAlong(b.direction.dup(), PADDLE_WIDTH * 2)
				if self.keyboardState[PLAYER_KEYS[pad.id][KEY_LAUNCH_BALL]] and pad.waitLaunch == 0:
					b.state = STATE_RUN
					pad.waitLaunch = PADDLE_LAUNCH_COOLDOWN

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

		# Draw team
		self.teamLeft.draw(self.win)
		self.teamRight.draw(self.win)

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
