from client_side.client_define import *
from client_side.vec2 import *
import client_side.hitbox as hitbox
import client_side.team as team
import client_side.ball as ball

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



class Client:
	def __init__(self):
		"""
		This method define all variables needed by the program
		"""
		# Init pygame
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

		# Creation of state list for player keys
		self.paddlesKeyState = PADDLES_KEYS_STATE.copy()

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
		self.powerUpEnable = False
		self.powerUp = [POWER_UP_SPAWN_COOLDOWN, hitbox.Hitbox(0, 0, (0, 0, 200), POWER_UP_HITBOX_COLOR), -1]
		for p in ball.getPointOfCircle(POWER_UP_HITBOX_RADIUS, POWER_UP_HITBOX_PRECISION, 0):
			self.powerUp[1].addPoint(p[0], p[1])

		# Walls creation
		self.walls = []

		# idPaddle, paddleTeam, Ball speed, Number of bounce, CC, Perfect shoot, time of goal
		self.goals = []

		self.ballNumber = 0

		# For communications
		# (Message type, message content)
		self.messageForServer = []
		# (Message type, message content)
		self.messageFromServer = []


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


	def step(self):
		"""
		This method is the main function of the game
		Call it in a while, it need to be re call until self.runMainLoop equals to False
		"""
		# Clear the message for server
		self.messageForServer.clear()

		self.parseMessageFromServer()
		# Game loop
		if self.runMainLoop:
			self.input()
			self.tick()
			self.render()
			# self.clock.tick(self.fps)

		# After compute it, clear message from the server
		self.messageFromServer.clear()


	def input(self):
		"""
		The method catch user's inputs, as key presse or a mouse click
		"""
		# We check each event
		for event in pg.event.get():
			# If the event it a click on the top right cross, we quit the game
			if event.type == pg.QUIT:
				self.runMainLoop = False

		self.keyboardState = pg.key.get_pressed()
		self.mouseState = pg.mouse.get_pressed()
		self.mousePos = pg.mouse.get_pos()

		# Press espace to quit
		if self.keyboardState[pg.K_ESCAPE]:
			self.runMainLoop = False

		# Update paddles keys
		for i in range(4):
			teamId = TEAM_LEFT
			if i >= TEAM_MAX_PLAYER:
				teamId = TEAM_RIGHT
			# {id_paddle, id_key, key_action [True = press, False = release]}
			templateContent = {"paddleId" : i, "keyId" : 0, "keyAction" : True}

			if self.keyboardState[PLAYER_KEYS[i][KEY_UP]] and not self.paddlesKeyState[i * 4 + KEY_UP]:
				self.paddlesKeyState[i * 4 + KEY_UP] = True
				content = templateContent.copy()
				content["keyId"] = KEY_UP
				content["keyAction"] = True
				self.messageForServer.append((CLIENT_MSG_TYPE_USER_EVENT, content))
			elif not self.keyboardState[PLAYER_KEYS[i][KEY_UP]] and self.paddlesKeyState[i * 4 + KEY_UP]:
				self.paddlesKeyState[i * 4 + KEY_UP] = False
				content = templateContent.copy()
				content["keyId"] = KEY_UP
				content["keyAction"] = False
				self.messageForServer.append((CLIENT_MSG_TYPE_USER_EVENT, content))

			if self.keyboardState[PLAYER_KEYS[i][KEY_DOWN]] and not self.paddlesKeyState[i * 4 + KEY_DOWN]:
				self.paddlesKeyState[i * 4 + KEY_DOWN] = True
				content = templateContent.copy()
				content["keyId"] = KEY_DOWN
				content["keyAction"] = True
				self.messageForServer.append((CLIENT_MSG_TYPE_USER_EVENT, content))
			elif not self.keyboardState[PLAYER_KEYS[i][KEY_DOWN]] and self.paddlesKeyState[i * 4 + KEY_DOWN]:
				self.paddlesKeyState[i * 4 + KEY_DOWN] = False
				content = templateContent.copy()
				content["keyId"] = KEY_DOWN
				content["keyAction"] = False
				self.messageForServer.append((CLIENT_MSG_TYPE_USER_EVENT, content))

			if self.keyboardState[PLAYER_KEYS[i][KEY_POWER_UP]] and not self.paddlesKeyState[i * 4 + KEY_POWER_UP]:
				self.paddlesKeyState[i * 4 + KEY_POWER_UP] = True
				content = templateContent.copy()
				content["keyId"] = KEY_POWER_UP
				content["keyAction"] = True
				self.messageForServer.append((CLIENT_MSG_TYPE_USER_EVENT, content))
			elif not self.keyboardState[PLAYER_KEYS[i][KEY_POWER_UP]] and self.paddlesKeyState[i * 4 + KEY_POWER_UP]:
				self.paddlesKeyState[i * 4 + KEY_POWER_UP] = False
				content = templateContent.copy()
				content["keyId"] = KEY_POWER_UP
				content["keyAction"] = False
				self.messageForServer.append((CLIENT_MSG_TYPE_USER_EVENT, content))

			if self.keyboardState[PLAYER_KEYS[i][KEY_LAUNCH_BALL]] and not self.paddlesKeyState[i * 4 + KEY_LAUNCH_BALL]:
				self.paddlesKeyState[i * 4 + KEY_LAUNCH_BALL] = True
				content = templateContent.copy()
				content["keyId"] = KEY_LAUNCH_BALL
				content["keyAction"] = True
				self.messageForServer.append((CLIENT_MSG_TYPE_USER_EVENT, content))
			elif not self.keyboardState[PLAYER_KEYS[i][KEY_LAUNCH_BALL]] and self.paddlesKeyState[i * 4 + KEY_LAUNCH_BALL]:
				self.paddlesKeyState[i * 4 + KEY_LAUNCH_BALL] = False
				content = templateContent.copy()
				content["keyId"] = KEY_LAUNCH_BALL
				content["keyAction"] = False
				self.messageForServer.append((CLIENT_MSG_TYPE_USER_EVENT, content))


	def tick(self):
		"""
		This is the method where all calculations will be done
		"""
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		self.time += delta

		# Check if ball move. If no ball move, all time base event are stopping
		if self.powerUpEnable:
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

		self.teamLeft.tick(delta, self.paddlesKeyState, updateTime)
		self.teamRight.tick(delta, self.paddlesKeyState, updateTime)

		ballToDelete = []

		for i in range(len(self.balls)):
			b = self.balls[i]
			b.updatePosition(delta, self.teamLeft.paddles, self.teamRight.paddles, self.walls, self.powerUp)
			if updateTime:
				b.updateTime(delta)

			# if the ball is in left goal
			if b.state == STATE_IN_GOAL_LEFT:
				self.ballInLeftGoal(b, i, ballToDelete)

			# if the ball is in right goal
			elif b.state == STATE_IN_GOAL_RIGHT:
				self.ballInRightGoal(b, i, ballToDelete)

			# case of ball follow player
			elif b.state == STATE_IN_FOLLOW:
				if b.lastPaddleTeam == TEAM_LEFT:
					pad = self.teamLeft.paddles[b.lastPaddleHitId]
				else:
					pad = self.teamRight.paddles[b.lastPaddleHitId]
				b.setPos(pad.pos.dup())
				b.pos.translateAlong(b.direction.dup(), PADDLE_WIDTH * 2)
				id = pad.id
				if pad.team == TEAM_RIGHT:
					id += TEAM_MAX_PLAYER
				if self.paddlesKeyState[id * 4 + KEY_LAUNCH_BALL] and pad.waitLaunch == 0:
					b.state = STATE_RUN
					pad.waitLaunch = PADDLE_LAUNCH_COOLDOWN

			# case of ball is Moving
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

		for i in range(len(ballToDelete)):
			self.balls.pop(ballToDelete[i] - i)

		# Verify if power can be use, and use it if possible
		if self.powerUpEnable and updateTime:
			if self.powerUp[0] == POWER_UP_TAKE:
				# Generate power up
				powerUp = random.randint(0, 12)
				if b.lastPaddleTeam == TEAM_LEFT:
					self.teamLeft.paddles[self.powerUp[2]].powerUp = powerUp
				else:
					self.teamRight.paddles[self.powerUp[2]].powerUp = powerUp
				self.powerUp[0] = POWER_UP_SPAWN_COOLDOWN

		if self.teamLeft.score >= TEAM_WIN_SCORE or self.teamRight.score >= TEAM_WIN_SCORE:
			self.quit()

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
		self.runMainLoop = False
		# pg.quit()
		# sys.exit()


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


	def ballInLeftGoal(self, ball:ball.Ball, i:int, ballToDelete:list):
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
			p.powerUp = random.randint(0, 12)

		if len(self.balls) - len(ballToDelete) > 1:
			ballToDelete.append(i)
			return

		ball.direction = Vec2(1, 0)
		ball.speed = BALL_START_SPEED
		ball.state = STATE_IN_FOLLOW
		ball.modifierSkipCollision = False
		ball.lastPaddleHitId = random.choice(self.teamLeft.paddles).id
		ball.lastPaddleTeam = TEAM_LEFT


	def ballInRightGoal(self, ball:ball.Ball, i:int, ballToDelete:list):
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

		if len(self.balls) - len(ballToDelete) > 1:
			ballToDelete.append(i)
			return

		ball.direction = Vec2(-1, 0)
		ball.speed = BALL_START_SPEED
		ball.state = STATE_IN_FOLLOW
		ball.modifierSkipCollision = False
		ball.lastPaddleHitId = random.choice(self.teamRight.paddles).id
		ball.lastPaddleTeam = TEAM_RIGHT


	def parseMessageFromServer(self):
		for message in self.messageFromServer:
			if message[0] == SERVER_MSG_TYPE_CREATE_START_INFO:
				self.parseMessageStartInfo(message[1])
			elif message[0] == SERVER_MSG_TYPE_UPDATE_PADDLES:
				self.parseMessageForPaddles(message[1])
			elif message[0] == SERVER_MSG_TYPE_UPDATE_BALLS:
				self.parseMessageForBalls(message[1])
			elif message[0] == SERVER_MSG_TYPE_UPDATE_POWER_UP:
				self.parseMessageForPowerUp(message[1])


	def parseMessageStartInfo(self, messageContent:list[dict]):
		# Content of obstacles :
		# {
		# 	obstables : [ {position:[x, y], points:[[x, y]], color:(r, g, b)} ]
		# 	powerUp : True or False
		# }
		self.walls.clear()

		for content in messageContent["obstacles"]:
			x = AREA_RECT[0] + content["position"][0]
			y = AREA_RECT[1] + content["position"][1]
			obstacle = createObstacle(x, y, content["points"], content["color"])
			self.walls.append(obstacle)

		self.powerUpEnable = messageContent["powerUp"]


	def parseMessageForPaddles(self, messageContent:list[dict]):
		# Content of paddles :
		# [
		# 	{id_paddle, id_team, position:[x, y], size:[w, h], powerUp, powerUpInCharge}
		# ]
		for content in messageContent:
			x = AREA_RECT[0] + content["position"][0]
			y = AREA_RECT[1] + content["position"][1]

			if content["id_team"] == TEAM_LEFT:
				self.teamLeft.paddles[content["id_paddle"]].setPos(x, y)
				self.teamLeft.paddles[content["id_paddle"]].w = content["size"][0]
				self.teamLeft.paddles[content["id_paddle"]].h = content["size"][1]
				self.teamLeft.paddles[content["id_paddle"]].powerUp = content["powerUp"]
				self.teamLeft.paddles[content["id_paddle"]].powerUpInCharge = content["powerUpInCharge"]
			else:
				self.teamRight.paddles[content["id_paddle"]].setPos(x, y)
				self.teamRight.paddles[content["id_paddle"]].w = content["size"][0]
				self.teamRight.paddles[content["id_paddle"]].h = content["size"][1]
				self.teamRight.paddles[content["id_paddle"]].powerUp = content["powerUp"]
				self.teamRight.paddles[content["id_paddle"]].powerUpInCharge = content["powerUpInCharge"]


	def parseMessageForBalls(self, messageContent:list[dict]):
		# Content of balls :
		# [
		# 	{position:[x, y], direction:[x, y], speed, radius, state, last_paddle_hit_info:[id, team], modifier_state}
		# ]
		i = 0
		numberOfMessageBall = len(messageContent)
		while i < numberOfMessageBall:
			content = messageContent[i]
			x = AREA_RECT[0] + content["position"][0]
			y = AREA_RECT[1] + content["position"][1]

			# Update ball if exist
			if i < len(self.balls):
				b = self.balls[i]
				b.direction = Vec2(content["direction"][0], content["direction"][1])
				b.speed = content["speed"]
				b.radius = content["radius"]
				b.state = content["state"]
				b.lastPaddleHitId = content["last_paddle_hit_info"][0]
				b.lastPaddleTeam = content["last_paddle_hit_info"][1]
				b.setModifierByState(content["modifier_state"])

			# Create a new one instead
			else:
				b = ball.Ball(x, y)
				b.direction = Vec2(content["direction"][0], content["direction"][1])
				b.speed = content["speed"]
				b.radius = content["radius"]
				b.state = content["state"]
				b.lastPaddleHitId = content["last_paddle_hit_info"][0]
				b.lastPaddleTeam = content["last_paddle_hit_info"][1]
				b.setModifierByState(content["modifier_state"])
				self.balls.append(b)

			i += 1


	def parseMessageForPowerUp(self, messageContent:list[dict]):
		# Content of balls :
		# {position:[x, y], state}
		x = AREA_RECT[0] + messageContent["position"][0]
		y = AREA_RECT[1] + messageContent["position"][1]

		self.powerUp[0] = messageContent["state"]
		self.powerUp[1].setPos(Vec2(x, y))

