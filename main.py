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

		self.powerUp = [POWER_UP_COOLDOWN, hitbox.Hitbox(0, 0, (0, 0, 200), (200, 200, 200)), -1]
		for p in ball.getPointOfCircle(20, 16, 0):
			self.powerUp[1].addPoint(p[0], p[1])

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
			ball.getPointOfCircle(100, 32, 360 / 64),
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

		# Check if ball move. If no ball move, all time base event are stopping
		updateTime = False
		for b in self.balls:
			if b.state == STATE_RUN:
				updateTime = True
				break

		if self.inputWait > 0:
			self.inputWait -= delta
			if self.inputWait < 0:
				self.inputWait = 0

		if updateTime and self.powerUp[0] > POWER_UP_VISIBLE:
			self.powerUp[0] -= delta
			if self.powerUp[0] <= POWER_UP_VISIBLE:
				self.powerUp[0] = POWER_UP_VISIBLE
				self.createPowerUp()

		self.teamLeft.tick(delta, self.keyboardState, self.balls, updateTime)
		self.teamRight.tick(delta, self.keyboardState, self.balls, updateTime)

		for b in self.balls:
			b.updatePosition(delta, self.teamLeft.paddles, self.teamRight.paddles, self.walls, self.powerUp)
			if updateTime:
				b.updateTime(delta)

			# if the ball is in left goal
			if b.state == STATE_IN_GOAL_LEFT:
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

		# Verify if power can be use, and use it if possible
		self.checkPowerUp(self.teamLeft, self.teamRight)
		self.checkPowerUp(self.teamRight, self.teamLeft)


		if self.powerUp[0] == POWER_UP_TAKE:
			# Generate power up
			powerUp = random.randint(0, 12)
			if self.powerUp[2] < TEAM_MAX_PLAYER:
				self.teamLeft.paddles[self.powerUp[2]].powerUp = powerUp
			else:
				self.teamRight.paddles[self.powerUp[2] - TEAM_MAX_PLAYER].powerUp = powerUp
			self.powerUp[0] = POWER_UP_COOLDOWN

		pg.display.set_caption(str(self.clock.get_fps()))


	def render(self):
		"""
		This is the method where all graphic update will be done
		"""
		# We clean our screen with one color
		self.win.fill((0, 0, 0))

		# Draw area
		pg.draw.rect(self.win, AREA_COLOR, AREA_RECT)
		# pg.draw.rect(self.win, LEFT_TEAM_COLOR, LEFT_TEAM_RECT)
		# pg.draw.rect(self.win, MIDDLE_COLOR, MIDDLE_RECT)
		# pg.draw.rect(self.win, RIGTH_TEAM_COLOR, RIGTH_TEAM_RECT)

		# Draw walls
		for w in self.walls:
			w.drawFill(self.win)
			if DRAW_HITBOX:
				w.draw(self.win)

		# Power up draw
		if self.powerUp[0] == POWER_UP_VISIBLE:
			self.powerUp[1].drawFill(self.win)
			if DRAW_HITBOX:
				self.powerUp[1].draw(self.win)

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


	def createPowerUp(self):
		collide = True

		while collide:
			collide = False

			x = random.randint(LEFT_TEAM_RECT[0] + LEFT_TEAM_RECT[2], RIGTH_TEAM_RECT[0])
			y = random.randint(AREA_RECT[1], AREA_RECT[1] + AREA_RECT[3])

			self.powerUp[1].setPos(Vec2(x, y))

			for hit in self.walls:
				collide = self.powerUp[1].isInsideSurrondingBox(hit)
				if collide:
					break


	def checkPowerUp(self, team:team.Team, ennemyTeam:team.Team):
		# powerUpTryUse = [power up id, paddle id, power up used (bool)]
		for powerUpTryUse in team.powerUpTryUse:
			if powerUpTryUse[0] == POWER_UP_BALL_FAST:
				pass

			elif powerUpTryUse[0] == POWER_UP_BALL_WAVE:
				pass

			elif powerUpTryUse[0] == POWER_UP_BALL_INVISIBLE:
				pass

			elif powerUpTryUse[0] == POWER_UP_BALL_NO_COLLISION:
				pass

			elif powerUpTryUse[0] == POWER_UP_DUPLICATION_BALL:
				pass

			elif powerUpTryUse[0] == POWER_UP_BALL_SLOW:
				pass

			elif powerUpTryUse[0] == POWER_UP_BALL_STOP:
				pass

			elif powerUpTryUse[0] == POWER_UP_BALL_BIG:
				pass

			elif powerUpTryUse[0] == POWER_UP_BALL_LITTLE:
				pass

			elif powerUpTryUse[0] == POWER_UP_PADDLE_FAST:
				powerUpTryUse[2] = True
				team.applyPowerUpToPaddles(POWER_UP_PADDLE_FAST)

			elif powerUpTryUse[0] == POWER_UP_PADDLE_SLOW:
				powerUpTryUse[2] = True
				ennemyTeam.applyPowerUpToPaddles(POWER_UP_PADDLE_SLOW)

			elif powerUpTryUse[0] == POWER_UP_PADDLE_BIG:
				powerUpTryUse[2] = True
				team.applyPowerUpToPaddles(POWER_UP_PADDLE_BIG)

			elif powerUpTryUse[0] == POWER_UP_PADDLE_LITTLE:
				powerUpTryUse[2] = True
				ennemyTeam.applyPowerUpToPaddles(POWER_UP_PADDLE_LITTLE)



Game().run() # Start game
