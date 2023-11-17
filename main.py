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
		self.time = 0

		self.last = time.time()

		self.runMainLoop = True

		self.inputWait = 0

		# Team creation
		self.teamLeft = team.Team(1, TEAM_LEFT)
		self.teamRight = team.Team(1, TEAM_RIGHT)

		# Ball creation
		self.balls = [ball.Ball(WIN_WIDTH / 2, WIN_HEIGHT / 2)]

		# Ball begin left side
		if random.random() > 0.5:
			self.balls[0].lastPaddleHitId = random.choice(self.teamLeft.paddles).id
		# Ball begin right side
		else:
			self.balls[0].lastPaddleHitId = random.choice(self.teamRight.paddles).id
			self.balls[0].direction = Vec2(-1, 0)
			self.balls[0].lastPaddleTeam = TEAM_RIGHT

		# Power up creation
		self.powerUp = [POWER_UP_SPAWN_COOLDOWN, hitbox.Hitbox(0, 0, (0, 0, 200), POWER_UP_HITBOX_COLOR), -1]
		for p in ball.getPointOfCircle(POWER_UP_HITBOX_RADIUS, POWER_UP_HITBOX_PRECISION, 0):
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

		# idPaddle, paddleTeam, Ball speed, Number of bounce, CC, Perfect shoot, time of goal
		self.goals = []

		self.ballNumber = 0


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

		self.time += delta

		# Check if ball move. If no ball move, all time base event are stopping
		if POWER_UP_ENABLE:
			updateTime = False
			for b in self.balls:
				if b.state == STATE_RUN:
					updateTime = True
					break

		if self.inputWait > 0:
			self.inputWait -= delta
			if self.inputWait < 0:
				self.inputWait = 0

		if not updateTime and self.powerUp[0] != POWER_UP_SPAWN_COOLDOWN:
			self.powerUp[0] = POWER_UP_SPAWN_COOLDOWN

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
				self.ballInLeftGoal(b)

			# if the ball is in right goal
			elif b.state == STATE_IN_GOAL_RIGHT:
				self.ballInRightGoal(b)

			# case of ball follow player
			elif b.state == STATE_IN_FOLLOW:
				if b.lastPaddleTeam == TEAM_LEFT:
					pad = self.teamLeft.paddles[b.lastPaddleHitId]
				else:
					pad = self.teamRight.paddles[b.lastPaddleHitId]
				b.setPos(pad.pos.dup())
				b.pos.translateAlong(b.direction.dup(), PADDLE_WIDTH * 2)
				if self.keyboardState[PLAYER_KEYS[pad.id][KEY_LAUNCH_BALL]] and pad.waitLaunch == 0:
					b.state = STATE_RUN
					pad.waitLaunch = PADDLE_LAUNCH_COOLDOWN

			else:
				for w in self.walls:
					# if not b.modifierSkipCollision and b.hitbox.isInside(w) and not b.hitbox.isCollide(w):
					if not b.modifierSkipCollision and b.hitbox.isInside(w):
						outOfCenter = vec2Sub(b.pos, w.pos)
						if outOfCenter.norm() == 0:
							outOfCenter = Vec2(1, 0)
						outOfCenter.normalize()
						b.direction = outOfCenter
						if not b.hitbox.isCollide(w):
							dir = outOfCenter.dup()
							dir.multiply(BALL_RADIUS * 2 + 5)
							pos = vec2Add(b.pos, dir)
							b.setPos(pos)

		# Verify if power can be use, and use it if possible
		if POWER_UP_ENABLE and updateTime:
			self.checkPowerUp(self.teamLeft, LEFT_TEAM_RECT, self.teamRight, RIGTH_TEAM_RECT)
			self.checkPowerUp(self.teamRight, RIGTH_TEAM_RECT, self.teamLeft, LEFT_TEAM_RECT)

			if self.powerUp[0] == POWER_UP_TAKE:
				# Generate power up
				powerUp = random.randint(0, 12)
				if b.lastPaddleTeam == TEAM_LEFT:
					self.teamLeft.paddles[self.powerUp[2]].powerUp = powerUp
				else:
					self.teamRight.paddles[self.powerUp[2]].powerUp = powerUp
				self.powerUp[0] = POWER_UP_SPAWN_COOLDOWN

		if self.teamLeft.score >= TEAM_WIN_SCORE or self.teamRight.score >= TEAM_WIN_SCORE:
			self.printFinalStat()

		testLen = len(self.balls)
		if testLen!= self.ballNumber:
			self.ballNumber = testLen
			print("Number of balls :",self.ballNumber)

		pg.display.set_caption("time : " + str(self.time) + " | fps : " + str(self.clock.get_fps()))


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


	def checkPowerUp(self, team:team.Team, teamArea:tuple, ennemyTeam:team.Team, ennemyTeamArea:tuple):
		teamAreaNoBall = True
		ennemyTeamAreaNoBall = True

		for b in self.balls:
			if b.state == STATE_RUN:
				if b.pos.x >= teamArea[0] and b.pos.x <= teamArea[0] + teamArea[2]:
					teamAreaNoBall = False
				elif b.pos.x >= ennemyTeamArea[0] and b.pos.x <= ennemyTeamArea[0] + ennemyTeamArea[2]:
					ennemyTeamAreaNoBall = False

				if not teamAreaNoBall and not ennemyTeamAreaNoBall:
					break

		ballPowerUp = []

		# powerUpTryUse = [power up id, paddle id, power up used (bool)]
		for powerUpTryUse in team.powerUpTryUse:
			if powerUpTryUse[0] == POWER_UP_BALL_FAST:
				if teamAreaNoBall:
					powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_BALL_WAVE:
				if teamAreaNoBall:
					powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_BALL_INVISIBLE:
				if teamAreaNoBall:
					powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_BALL_NO_COLLISION:
				ballPowerUp.append(POWER_UP_BALL_NO_COLLISION)
				powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_DUPLICATION_BALL:
				if ennemyTeamAreaNoBall:
					newBalls = []
					for b in self.balls:
						if b.state == STATE_RUN:
							newBalls.append(b.dup())
					self.balls.extend(newBalls)
					powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_BALL_SLOW:
				ballPowerUp.append(POWER_UP_BALL_SLOW)
				powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_BALL_STOP:
				ballPowerUp.append(POWER_UP_BALL_STOP)
				powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_BALL_BIG:
				ballPowerUp.append(POWER_UP_BALL_BIG)
				powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_BALL_LITTLE:
				ballPowerUp.append(POWER_UP_BALL_LITTLE)
				powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_PADDLE_FAST:
				team.applyPowerUpToPaddles(POWER_UP_PADDLE_FAST)
				powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_PADDLE_SLOW:
				ennemyTeam.applyPowerUpToPaddles(POWER_UP_PADDLE_SLOW)
				powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_PADDLE_BIG:
				team.applyPowerUpToPaddles(POWER_UP_PADDLE_BIG)
				powerUpTryUse[2] = True

			elif powerUpTryUse[0] == POWER_UP_PADDLE_LITTLE:
				ennemyTeam.applyPowerUpToPaddles(POWER_UP_PADDLE_LITTLE)
				powerUpTryUse[2] = True

		for b in self.balls:
			for powerUp in ballPowerUp:
				if powerUp == POWER_UP_BALL_NO_COLLISION:
					b.modifierSkipCollision = True
				elif powerUp == POWER_UP_BALL_SLOW:
					b.addPowerUpEffect(POWER_UP_BALL_SLOW)
				elif powerUp == POWER_UP_BALL_STOP:
					b.modifierStopBallTimer += POWER_UP_BALL_STOP_TIMER_EFFECT
				elif powerUp == POWER_UP_BALL_BIG:
					b.addPowerUpEffect(POWER_UP_BALL_BIG)
				elif powerUp == POWER_UP_BALL_LITTLE:
					b.addPowerUpEffect(POWER_UP_BALL_LITTLE)


	def ballInLeftGoal(self, ball:ball.Ball):
		self.teamRight.score += 1
		# for stats
		contreCamp = False
		if ball.lastPaddleTeam == TEAM_LEFT:
			paddle = self.teamLeft.paddles[ball.lastPaddleHitId]
			paddle.numberOfContreCamp += 1
			contreCamp = True
		else:
			paddle = self.teamRight.paddles[ball.lastPaddleHitId]
		paddle.numberOfGoal += 1

		if ball.numberOfBounce > paddle.maxBounceBallGoal:
			paddle.maxBounceBallGoal = ball.numberOfBounce

		perfectShoot = False
		if ball.pos.y < AREA_RECT[1] + PERFECT_SHOOT_SIZE or ball.pos.y > AREA_RECT[1] + AREA_RECT[3] - PERFECT_SHOOT_SIZE:
			paddle.numberOfPerfectShoot += 1
			perfectShoot = True

		# idPaddle, paddleTeam, Ball speed, Number of bounce, CC, Perfect shoot, time of goal
		self.goals.append((paddle.id, paddle.team, ball.speed, ball.numberOfBounce, contreCamp, perfectShoot, self.time))

		for p in self.teamLeft.paddles:
			p.powerUp = powerUp = random.randint(0, 12)
		ball.direction = Vec2(1, 0)
		ball.speed = BALL_START_SPEED
		ball.state = STATE_IN_FOLLOW
		ball.modifierSkipCollision = False
		ball.lastPaddleHitId = random.choice(self.teamLeft.paddles).id
		ball.lastPaddleTeam = TEAM_LEFT


	def ballInRightGoal(self, ball:ball.Ball):
		self.teamLeft.score += 1
		# for stats
		contreCamp = False
		if ball.lastPaddleTeam == TEAM_LEFT:
			paddle = self.teamLeft.paddles[ball.lastPaddleHitId]
		else:
			paddle = self.teamRight.paddles[ball.lastPaddleHitId]
			paddle.numberOfContreCamp += 1
			contreCamp = True
		paddle.numberOfGoal += 1
		if ball.numberOfBounce > paddle.maxBounceBallGoal:
			paddle.maxBounceBallGoal = ball.numberOfBounce

		perfectShoot = False
		if ball.pos.y < AREA_RECT[1] + PERFECT_SHOOT_SIZE or ball.pos.y > AREA_RECT[1] + AREA_RECT[3] - PERFECT_SHOOT_SIZE:
			paddle.numberOfPerfectShoot += 1
			perfectShoot = True

		# idPaddle, paddleTeam, Ball speed, Number of bounce, CC, Perfect shoot, time of goal
		self.goals.append((paddle.id, paddle.team, ball.speed, ball.numberOfBounce, contreCamp, perfectShoot, self.time))

		for p in self.teamRight.paddles:
			p.powerUp = random.randint(0, 12)
		ball.direction = Vec2(-1, 0)
		ball.speed = BALL_START_SPEED
		ball.state = STATE_IN_FOLLOW
		ball.modifierSkipCollision = False
		ball.lastPaddleHitId = random.choice(self.teamRight.paddles).id
		ball.lastPaddleTeam = TEAM_RIGHT


	def printFinalStat(self):
		if self.teamLeft.score > self.teamRight.score:
			print("Team left win !")
		else:
			print("Team right win !")

		print("=====================================")
		print("|             GAME STATS            |")
		print("=====================================")
		print("Team left score :", self.teamLeft.score)
		print("Team right score :", self.teamRight.score)
		print("Team left number of player :", len(self.teamLeft.paddles))
		print("Team right number of player :", len(self.teamRight.paddles))
		print("Number of ball :", len(self.balls))
		print()
		print("=====================================")
		print("|           PADDLES STATS           |")
		print("=====================================")
		print("Team left players :")
		print("\t---------------------------")
		for p in self.teamLeft.paddles:
			print("\tPaddle id :", p.id)
			print("\tNumber of goal :", p.numberOfGoal)
			print("\tMax speed ball touch :", p.maxSpeedBallTouch)
			print("\tMax bounce of goal ball :", p.maxBounceBallGoal)
			print("\tNumber of CC :", p.numberOfContreCamp)
			print("\tNumber of perfect shoot :", p.numberOfPerfectShoot)
			print("\t---------------------------")
		print("Team right players :")
		print("\t---------------------------")
		for p in self.teamRight.paddles:
			print("\tPaddle id :", p.id)
			print("\tNumber of goal :", p.numberOfGoal)
			print("\tMax speed ball touch :", p.maxSpeedBallTouch)
			print("\tMax bounce of goal ball :", p.maxBounceBallGoal)
			print("\tNumber of CC :", p.numberOfContreCamp)
			print("\tNumber of perfect shoot :", p.numberOfPerfectShoot)
			print("\t---------------------------")
		print()
		print("=====================================")
		print("|            BALLS STATS            |")
		print("=====================================")
		# idPaddle, paddleTeam, Ball speed, Number of bounce, CC, Perfect shoot, time of goal
		for goal in self.goals:
			print("Paddle id :", goal[0])
			print("Paddle team :", goal[1])
			print("Ball speed ball :", goal[2])
			print("Number of bounce :", goal[3])
			print("Is CC :", goal[4])
			print("Is Perfect Shoot :", goal[5])
			print("Time :", goal[6])
			print("---------------------------")



		self.quit()




Game().run() # Start game
