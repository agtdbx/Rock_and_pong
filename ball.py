from define import *
from vec2 import *
import hitbox
import paddle

import pygame as pg



def getPointOfCircle(radius, precision, beginDegree = 0):
	points = []
	for i in range(precision):
			degree = 360 / precision * i + beginDegree
			radian = degree * (math.pi / 180)
			x = radius * math.cos(radian)
			y = radius * math.sin(radian)
			points.append((x, y))
	return points



class Ball:
	def __init__(self, x, y):
		self.pos = Vec2(x, y)
		self.radius = BALL_RADIUS
		self.color = BALL_COLOR
		self.originalSprite = pg.image.load("imgs/ball.png")
		self.sprite = pg.transform.scale(self.originalSprite, (self.radius * 2, self.radius * 2))
		self.hitbox = hitbox.Hitbox(self.pos.x, self.pos.y, HITBOX_BALL_COLOR)

		# Modifier
		self.modifierSpeed = 1
		self.modifierSize = 1
		self.modifierSkipCollision = False
		self.modifierPhatomBall = False
		self.modifierPhatomBallTimer = -1

		self.resetHitbox()

		self.speed = BALL_START_SPEED
		self.direction = Vec2(1, 0)

		self.lastPositions = [(x, y) for _ in range(BALL_TRAIL_LENGTH)]
		self.lastColors = [BALL_COLOR for _ in range(BALL_TRAIL_LENGTH)]
		self.state = STATE_IN_FOLLOW

		self.lastPaddleHitId = 1


	def resetHitbox(self):
		self.hitbox.setPos(self.pos)
		self.hitbox.clearPoints()
		points = getPointOfCircle(self.radius * self.modifierSize, BALL_HITBOX_PRECISION, 360 / (BALL_HITBOX_PRECISION * 2))

		for p in points:
			self.hitbox.addPoint(p[0], p[1])


	def resetModifier(self):
		self.modifierSpeed = 1
		if self.modifierSize != 1:
			self.modifySize(1)
		self.modifierSkipCollision = False
		self.modifierPhatomBall = False
		self.modifierPhatomBallTimer = -1


	def modifySize(self, modifier):
		self.modifierSize = modifier
		self.sprite = pg.transform.scale(self.originalSprite, ((self.radius * 2) * self.modifierSize, (self.radius * 2) * self.modifierSize))
		self.resetHitbox()


	def draw(self, win):
		for i in range(BALL_TRAIL_LENGTH):
			gradiant = i / BALL_TRAIL_LENGTH
			color = (int(self.lastColors[i][0] * BALL_TRAIL_OPACITY),
					int(self.lastColors[i][1] * BALL_TRAIL_OPACITY),
					int(self.lastColors[i][2] * BALL_TRAIL_OPACITY))
			if not self.modifierPhatomBall or int(self.modifierPhatomBallTimer * 5) % 2:
				pg.draw.circle(win, color, self.lastPositions[i], (self.radius * gradiant) * self.modifierSize)

		if not self.modifierPhatomBall or int(self.modifierPhatomBallTimer * 5) % 2:
			win.blit(self.sprite, (self.pos.x - (self.radius * self.modifierSize), self.pos.y - (self.radius * self.modifierSize)))
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


	def updateTime(self, detla):
		if self.modifierPhatomBallTimer != -1:
			self.modifierPhatomBallTimer += detla


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
		deltaSpeed = self.speed * delta * self.modifierSpeed

		nbCheckCollisionStep = int(deltaSpeed // BALL_MOVE_STEP)
		lastStepMove = deltaSpeed - (nbCheckCollisionStep * BALL_MOVE_STEP)
		for i in range(nbCheckCollisionStep + 1):
			step = BALL_MOVE_STEP
			if i == nbCheckCollisionStep:
				step = lastStepMove

			newpos = self.pos.dup()
			newpos.translateAlong(self.direction, step)
			self.hitbox.setPos(newpos)

			collision = False

			# Collision with paddle
			for p in paddles:
				if collision:
					newpos = self.pos.dup()
					newpos.translateAlong(self.direction, step)
					collision = False
				collision = self.makeCollisionWithPaddle(p)

			# Collision with wall
			for w in walls:
				if collision:
					newpos = self.pos.dup()
					newpos.translateAlong(self.direction, step)
				collision = self.makeCollisionWithWall(w)

			if collision:
				newpos = self.pos.dup()
				newpos.translateAlong(self.direction, step)

			# Check if ball is in goal
			if newpos.x - self.radius < AREA_RECT[0]:
				self.state = STATE_IN_GOAL_LEFT
				self.resetModifier()
				return

			if newpos.x + self.radius > AREA_RECT[0] + AREA_RECT[2]:
				self.state = STATE_IN_GOAL_RIGHT
				self.resetModifier()
				return

			# Teleport from up to down
			if newpos.y + self.radius < AREA_RECT[1]:
				newpos.y += AREA_RECT[3]
				self.resetHitbox()
			# Teleport from down to up
			elif newpos.y - self.radius > AREA_RECT[1] + AREA_RECT[3]:
				newpos.y -= AREA_RECT[3]
				self.resetHitbox()

			# Affect position along direction and
			self.pos = newpos.dup()
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


	def makeCollisionWithWall(self, hitbox:hitbox.Hitbox):
		if self.modifierSkipCollision or not hitbox.isCollide(self.hitbox):
			return False

		collideInfos = hitbox.getCollideInfo(self.hitbox)

		for collideInfo in collideInfos:
			if collideInfo[0]:
				p0 = collideInfo[1]
				p1 = collideInfo[2]
				normal = getNormalOfSegment(p0, p1)
				last = self.direction
				self.direction = reflectionAlongVec2(normal, self.direction)
				if last != self.direction:
					self.speed += BALL_WALL_ACCELERATION
					if self.speed > BALL_MAX_SPEED:
						self.speed = BALL_MAX_SPEED
					return True
		return False


	def makeCollisionWithPaddle(self, paddle:paddle.Paddle):
		if not paddle.hitbox.isCollide(self.hitbox):
			return False

		newDir = self.pos.dup()
		newDir.subBy(paddle.pos)
		newDir.normalize()

		self.direction = newDir

		self.speed += BALL_PADDLE_ACCELERATION
		if self.speed > BALL_MAX_SPEED:
			self.speed = BALL_MAX_SPEED

		self.lastPaddleHitId = paddle.id

		self.resetModifier()

		return True


	def dup(self):
		ball = Ball(self.pos.x, self.pos.y)
		ball.direction = self.direction.dup()
		self.speed /= 2
		if self.speed < BALL_MIN_SPEED:
			self.speed = BALL_MIN_SPEED
		ball.speed = self.speed

		self.direction.rotate(30)
		ball.direction.rotate(-30)

		ball.state = STATE_RUN

		return ball
