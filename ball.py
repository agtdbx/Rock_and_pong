from define import *
from vec2 import *
import hitbox
import paddle

import pygame as pg
import random


class Ball:
	def __init__(self, x, y):
		self.pos = Vec2(x, y)
		self.radius = BALL_RADIUS
		self.color = BALL_COLOR
		self.sprite = pg.image.load("imgs/ball.png")
		self.hitbox = hitbox.Hitbox(x, y, HITBOX_BALL_COLOR)

		for i in range(BALL_HITBOX_PRECISION):
			degree = 360 / BALL_HITBOX_PRECISION * i
			radian = degree * (math.pi / 180)
			x = BALL_RADIUS * math.cos(radian)
			y = BALL_RADIUS * math.sin(radian)
			self.hitbox.addPoint(x, y)

		self.speed = BALL_START_SPEED
		self.direction = Vec2(random.randint(-1, 1) * 10, random.randint(-10, 10))
		if self.direction.x == 0:
			self.direction.x = -10
		self.direction.normalize()
		self.lastPositions = [(x, y) for _ in range(BALL_TRAIL_LENGTH)]
		self.lastColors = [BALL_COLOR for _ in range(BALL_TRAIL_LENGTH)]
		self.state = STATE_RUN

		self.lastPaddleHitId = 0


	def draw(self, win):
		for i in range(BALL_TRAIL_LENGTH):
			gradiant = i / BALL_TRAIL_LENGTH
			color = (int(self.lastColors[i][0] * BALL_TRAIL_OPACITY),
					int(self.lastColors[i][1] * BALL_TRAIL_OPACITY),
					int(self.lastColors[i][2] * BALL_TRAIL_OPACITY))
			pg.draw.circle(win, color, self.lastPositions[i], self.radius * gradiant)

		win.blit(self.sprite, (self.pos.x - self.radius, self.pos.y - self.radius))
		self.hitbox.draw(win)


	def affecteDirection(self, mousePos):
		if self.state != STATE_RUN:
			return

		vecDir = Vec2(mousePos[0] - self.pos.x, mousePos[1] - self.pos.y)
		norm = vecDir.norm()
		vecDir.divide(norm)

		if norm != 0:
			self.speed += norm
			if self.speed > BALL_MAX_SPEED:
				self.speed = BALL_MAX_SPEED

			self.direction.add(vecDir)
			self.direction.normalize()


	def updatePosition(self, delta, paddles, walls):
		if self.state != STATE_RUN:
			return

		# Store last positions
		for i in range (1, BALL_TRAIL_LENGTH):
			self.lastPositions[i - 1] = self.lastPositions[i]
		self.lastPositions[-1] = self.pos.asTupple()

		# Store last colors
		for i in range (1, BALL_TRAIL_LENGTH):
			self.lastColors[i - 1] = self.lastColors[i]
		self.lastColors[-1] = self.color

		# Check position along direction and speed
		deltaSpeed = self.speed * delta
		newpos = self.pos.dup()
		newpos.translateAlong(self.direction, deltaSpeed)
		self.hitbox.setPos(newpos)

		# Collision with paddle
		for p in paddles:
			self.makeCollisionWithPaddle(p)

		# Collision with wall
		for w in walls:
			self.makeCollisionWithWall(w)

		newpos = self.pos.dup()
		newpos.translateAlong(self.direction, deltaSpeed)

		# Check if ball is in goal
		if newpos.x - self.radius < AREA_RECT[0]:
			self.state = STATE_IN_GOAL_LEFT
			return

		if newpos.x + self.radius > AREA_RECT[0] + AREA_RECT[2]:
			self.state = STATE_IN_GOAL_RIGHT
			return

		# Teleport into the other x wall
		if newpos.y + self.radius < AREA_RECT[1]:
			newpos.y += AREA_RECT[3]
		elif newpos.y - self.radius > AREA_RECT[1] + AREA_RECT[3]:
			newpos.y -= AREA_RECT[3]

		# Affect position along direction and
		self.pos = newpos
		self.hitbox.setPos(self.pos)

		if self.speed < BALL_MAX_SPEED / 2:
			green_gradient = 1 - self.speed / BALL_MAX_SPEED
			blue_gradient = 1 - self.speed / BALL_MAX_SPEED
		else:
			green_gradient = self.speed / BALL_MAX_SPEED
			blue_gradient = 1 - self.speed / BALL_MAX_SPEED
		self.color =	(BALL_COLOR[0],
						BALL_COLOR[1] * green_gradient,
						BALL_COLOR[2] * blue_gradient)

		# Friction
		if BALL_FRICTION and self.speed > 0:
			self.speed -= max(BALL_MINIMUM_FRICTION, (self.speed * BALL_FRICTION_STRENGTH)) * delta
			if self.speed < 0:
				self.speed = 0


	def setPos(self, pos):
		self.pos = pos
		for i in range(BALL_TRAIL_LENGTH):
			self.lastColors[i] = self.color
			self.lastPositions[i] = self.pos.asTupple()


	def makeCollisionWithWall(self, hitbox):
		if not hitbox.isCollide(self.hitbox):
			return

		collideInfos = hitbox.getCollideInfo(self.hitbox)

		for collideInfo in collideInfos:
			if collideInfo[0]:
				p0 = collideInfo[1]
				p1 = collideInfo[2]
				normal = getNormalOfSegment(p0, p1)
				last = self.direction
				self.direction = reflectionAlongVec2(normal, self.direction)
				if last != self.direction:
					break


	def makeCollisionWithPaddle(self, paddle:paddle.Paddle):
		if not paddle.hitbox.isCollide(self.hitbox):
			return

		newDir = self.pos.dup()
		newDir.subBy(paddle.pos)
		newDir.normalize()

		self.direction = newDir

		self.speed += self.speed * BALL_ACCELERATION
		if self.speed > BALL_MAX_SPEED:
			self.speed = BALL_MAX_SPEED

		self.lastPaddleHitId = paddle.id


	def dup(self):
		ball = Ball(self.pos.x, self.pos.y)
		ball.direction = self.direction.dup()
		ball.speed = self.speed

		self.direction.rotate(45)
		ball.direction.rotate(-45)

		return ball
