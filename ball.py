from define import *
from vec2 import *
import hitbox

import pygame as pg

class Ball:
	def __init__(self, x, y):
		self.pos = Vec2(x, y)
		self.radius = BALL_RADIUS
		self.color = BALL_COLOR
		self.sprite = pg.image.load("imgs/ball.png")
		self.hitbox = hitbox.Hitbox(x, y, HITBOX_BALL_COLOR)
		self.hitbox.addPoint(0, -18.5)
		self.hitbox.addPoint(11.5, - 14.5)
		self.hitbox.addPoint(18.5, - 5.5)
		self.hitbox.addPoint(17.5, 7.5)
		self.hitbox.addPoint(11.5, 15.5)
		self.hitbox.addPoint(0, 18.5)
		self.hitbox.addPoint(-10.5, 15.5)
		self.hitbox.addPoint(-16.5, 6.5)
		self.hitbox.addPoint(-16.5, -6.5)
		self.hitbox.addPoint(-9.5, -13.5)
		self.speed = 0
		self.direction = Vec2(0, 0)
		self.lastPositions = [(x, y) for _ in range(BALL_TRAIL_LENGTH)]
		self.lastColors = [BALL_COLOR for _ in range(BALL_TRAIL_LENGTH)]
		self.inWaiting = False


	def draw(self, win):
		if self.inWaiting:
			return

		for i in range(BALL_TRAIL_LENGTH):
			gradiant = i / BALL_TRAIL_LENGTH
			color = (int(self.lastColors[i][0] * BALL_TRAIL_OPACITY),
					int(self.lastColors[i][1] * BALL_TRAIL_OPACITY),
					int(self.lastColors[i][2] * BALL_TRAIL_OPACITY))
			pg.draw.circle(win, color, self.lastPositions[i], self.radius * gradiant)

		win.blit(self.sprite, (self.pos.x - self.radius, self.pos.y - self.radius))
		self.hitbox.draw(win)


	def affecteDirection(self, mousePos):
		if self.inWaiting:
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


	def updatePosition(self, delta, walls):
		if self.inWaiting:
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

		# Collision with wall
		newpos = self.pos.dup()
		newpos.translateAlong(self.direction, deltaSpeed)
		self.hitbox.setPos(newpos.x, newpos.y)
		for w in walls:
			w.makeCollisionWithBall(self)

		newpos = self.pos.dup()
		newpos.translateAlong(self.direction, deltaSpeed)

		# Ball in goal
		if newpos.x - self.radius < AREA_RECT[0] or newpos.x + self.radius > AREA_RECT[0] + AREA_RECT[2]:
			self.inWaiting = True

		# Teleport into the other x wall
		if newpos.y + self.radius < AREA_RECT[1]:
			newpos.y += AREA_BORDER_RECT[3]
		elif newpos.y - self.radius > AREA_RECT[1] + AREA_RECT[3]:
			newpos.y -= AREA_BORDER_RECT[3]

		# Affect position along direction and
		self.pos = newpos

		self.hitbox.setPos(self.pos.x, self.pos.y)

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
		if self.speed > 0:
			self.speed -= max(BALL_MINIMUM_FRICTION, (self.speed * BALL_FRICTION_STRENGTH)) * delta
			if self.speed < 0:
				self.speed = 0
