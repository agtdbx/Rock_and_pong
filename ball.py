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
		# Geometry
		self.pos = Vec2(x, y)
		self.radius = BALL_RADIUS
		self.speed = BALL_START_SPEED
		self.direction = Vec2(1, 0)

		# Graphique
		self.color = BALL_COLOR
		self.originalSprite = pg.image.load("imgs/ball.png")
		self.sprite = pg.transform.scale(self.originalSprite, (self.radius * 2, self.radius * 2))

		# Hitbox creation
		self.hitbox = hitbox.Hitbox(self.pos.x, self.pos.y, HITBOX_BALL_COLOR)
		self.hitbox.setPos(self.pos)
		points = getPointOfCircle(self.radius, BALL_HITBOX_PRECISION, 360 / (BALL_HITBOX_PRECISION * 2))

		for p in points:
			self.hitbox.addPoint(p[0], p[1])

		# Modifier
		self.modifierSpeed = 1
		self.modifierSize = 1
		self.modifierSkipCollision = False
		self.modifierInvisibleBall = False
		self.modifierInvisibleBallTimer = 0
		self.modifierWaveBall = False
		self.modifierWaveBallTimer = 0
		self.modifierStopBallTimer = 0

		# Represente the effect on ball [POWER_UP, TIME_EFFECT]
		self.powerUpEffects = []

		self.lastPositions = [(x, y) for _ in range(BALL_TRAIL_LENGTH)]
		self.lastColors = [BALL_COLOR for _ in range(BALL_TRAIL_LENGTH)]
		self.state = STATE_IN_FOLLOW

		self.lastPaddleHitId = 1

		# For stat
		self.numberOfBounce = 0


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
		self.modifierInvisibleBall = False
		self.modifierInvisibleBallTimer = 0
		self.modifierWaveBall = False
		self.modifierWaveBallTimer = 0


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
			if not self.modifierInvisibleBall or int(self.modifierInvisibleBallTimer * 5) % 2:
				pg.draw.circle(win, color, self.lastPositions[i], (self.radius * gradiant) * self.modifierSize)

		if not self.modifierInvisibleBall or int(self.modifierInvisibleBallTimer * POWER_UP_BALL_INVISIBLE_SPEED_FACTOR) % 2:
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


	def updateTime(self, delta):
		if self.modifierInvisibleBall:
			self.modifierInvisibleBallTimer += delta

		if self.modifierWaveBall:
			self.modifierWaveBallTimer += delta

		if self.modifierStopBallTimer > 0:
			self.modifierStopBallTimer -= delta
			if self.modifierStopBallTimer < 0:
				self.modifierStopBallTimer = 0

		powerUpEffectToRemove = []

		for i in range(len(self.powerUpEffects)):
			powerUpEffect = self.powerUpEffects[i]
			if powerUpEffect[1] > 0:
				powerUpEffect[1] -= delta
				# If the time of the power up ended
				if powerUpEffect[1] < 0:
					powerUpEffect[1] = 0
					powerUpEffectToRemove.append(i)
					# Remove the effect of the power up

					if powerUpEffect[0] == POWER_UP_BALL_SLOW:
						self.modifierSpeed *= POWER_UP_BALL_SLOW_SPEED_FACTOR
						if self.modifierSpeed > 1:
							self.modifierSpeed = 1

					elif powerUpEffect[0] == POWER_UP_BALL_BIG:
						self.modifierSize /= POWER_UP_BALL_BIG_SIZE_FACTOR
						self.modifySize(self.modifierSize)

					elif powerUpEffect[0] == POWER_UP_BALL_LITTLE:
						self.modifierSize *= POWER_UP_BALL_LITTLE_SIZE_FACTOR
						self.modifySize(self.modifierSize)

		for i in range(len(powerUpEffectToRemove)):
			self.powerUpEffects.pop(powerUpEffectToRemove[i] - i)


	def getRealDirection(self) -> Vec2:
		if not self.modifierWaveBall:
			return self.direction

		realDirection = self.direction.dup()
		realDirection.rotate(POWER_UP_BALL_WAVE_DEGREES * math.sin(self.modifierWaveBallTimer * POWER_UP_BALL_WAVE_SPEED_FACTOR))

		return realDirection


	def updatePosition(self, delta, paddlesLeft, paddlesRight, walls, powerUp):
		if self.state != STATE_RUN or self.modifierStopBallTimer > 0:
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

			realDirection = self.getRealDirection()
			newpos = self.pos.dup()
			newpos.translateAlong(realDirection, step)
			self.hitbox.setPos(newpos)

			collision = False

			# Collision with powerUp
			if powerUp[0] == POWER_UP_VISIBLE and self.hitbox.isCollide(powerUp[1]):
				powerUp[0] = POWER_UP_TAKE
				powerUp[2] = self.lastPaddleHitId

			# Collision with paddle
			for p in paddlesLeft:
				if collision:
					realDirection = self.getRealDirection()
					newpos = self.pos.dup()
					newpos.translateAlong(realDirection, step)
					collision = False
				collision = self.makeCollisionWithPaddle(p)

			for p in paddlesRight:
				if collision:
					realDirection = self.getRealDirection()
					newpos = self.pos.dup()
					newpos.translateAlong(realDirection, step)
					collision = False
				collision = self.makeCollisionWithPaddle(p)

			# Collision with wall
			for w in walls:
				if collision:
					realDirection = self.getRealDirection()
					newpos = self.pos.dup()
					newpos.translateAlong(realDirection, step)
					collision = False
				collision = self.makeCollisionWithWall(w)

			if collision:
				realDirection = self.getRealDirection()
				newpos = self.pos.dup()
				newpos.translateAlong(realDirection, step)

			# Check if ball is in goal
			if newpos.x - self.radius < AREA_RECT[0]:
				self.state = STATE_IN_GOAL_LEFT
				self.resetModifier()
				self.powerUpEffects.clear()
				return

			if newpos.x + self.radius > AREA_RECT[0] + AREA_RECT[2]:
				self.state = STATE_IN_GOAL_RIGHT
				self.resetModifier()
				self.powerUpEffects.clear()
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

		# Trail color
		# If the ball is faster than normal, change tail color
		if self.modifierSpeed > 1:
			self.color =	(BALL_COLOR[0] * green_gradient,
							BALL_COLOR[1] * blue_gradient,
							BALL_COLOR[2])
		# Idem if slower
		elif self.modifierSpeed < 1:
			self.color =	(BALL_COLOR[0] * blue_gradient,
							BALL_COLOR[1],
							BALL_COLOR[2]* green_gradient)
		else:
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
		if self.modifierSkipCollision:
			return False

		if not hitbox.isCollide(self.hitbox):
			return False

		collideInfos = hitbox.getCollideInfo(self.hitbox)

		collide = False

		hitPos = []
		newDirections = []

		nbCollide = 0
		for collideInfo in collideInfos:
			if collideInfo[0]:
				hitPos.append(collideInfo[3])
				nbCollide += 1
				p0 = collideInfo[1]
				p1 = collideInfo[2]
				normal = getNormalOfSegment(p0, p1)
				direction = reflectionAlongVec2(normal, self.direction)
				newDirections.append(direction.dup())
				self.speed += BALL_WALL_ACCELERATION
				if self.speed > BALL_MAX_SPEED:
					self.speed = BALL_MAX_SPEED
				self.modifierWaveBall = False
				self.modifierWaveBallTimer = 0
				if self.modifierSpeed > 1:
					self.modifierSpeed = 1
				# Bounce stat
				self.numberOfBounce += 1
				collide = True

		# print("Pos ball")
		# print(self.pos)
		# print("Hitbox ball")
		# print(self.hitbox)
		# print("Hitbox wall")
		# print(hitbox)
		# print("Number of collide :", nbCollide)
		# print("Collision :", collide)
		# print()
		# print("hit pos :")
		# for pos in hitPos:
		# 	print(pos)
		# print()
		# print()

		if len(newDirections) == 1:
			self.direction = newDirections[0].dup()
		elif len(newDirections) > 1:
			p1 = hitPos[0]
			p2 = hitPos[1]
			normal = getNormalOfSegment(p1, p2)
			self.direction = reflectionAlongVec2(normal, self.direction)

		return collide


	def makeCollisionWithPaddle(self, paddle:paddle.Paddle):
		if not paddle.hitbox.isCollide(self.hitbox):
			return False

		# Speed stat
		realSpeed = self.speed * self.modifierSpeed
		if realSpeed > paddle.maxSpeedBallTouch:
			paddle.maxSpeedBallTouch = realSpeed

		# Bounce stat
		self.numberOfBounce = 0

		# New dir of ball
		diffY = self.pos.y - paddle.pos.y
		diffY /= (paddle.h * paddle.modifierSize) / 2

		if paddle.pos.x < self.pos.x:
			newDir = Vec2(1, diffY)
		else:
			newDir = Vec2(-1, diffY)

		newDir.normalize()
		self.direction = newDir

		# Accelerate ball after hit paddle
		self.speed += BALL_PADDLE_ACCELERATION
		if self.speed > BALL_MAX_SPEED:
			self.speed = BALL_MAX_SPEED

		self.lastPaddleHitId = paddle.id

		# Reset modifier
		self.modifierSkipCollision = False

		self.modifierInvisibleBall = False
		self.modifierInvisibleBallTimer = 0

		self.modifierWaveBall = False
		self.modifierWaveBallTimer = 0
		if self.modifierSpeed > 1:
			self.modifierSpeed = 1

		# If the paddle have power up in charge, apply them to the ball
		if len(paddle.powerUpInCharge) > 0:
			for powerUp in paddle.powerUpInCharge:
				if powerUp == POWER_UP_BALL_FAST:
					self.modifierSpeed *= POWER_UP_BALL_FAST_FACTOR
					self.modifierStopBallTimer = POWER_UP_BALL_FAST_TIME_STOP
					for i in range(len(self.lastPositions)):
						self.lastPositions[i] = self.pos.asTupple()

				elif powerUp == POWER_UP_BALL_WAVE:
					self.modifierWaveBall = True

				elif powerUp == POWER_UP_BALL_INVISIBLE:
					self.modifierInvisibleBall = True

			paddle.powerUpInCharge.clear()

		return True


	def dup(self):
		# Create new ball
		ball = Ball(self.pos.x, self.pos.y)

		# Dup direction
		ball.direction = self.direction.dup()

		# Set new speed
		self.speed /= POWER_UP_DUPLICATION_BALL_SPEED_REDUCE_FACTOR
		if self.speed < BALL_MIN_SPEED:
			self.speed = BALL_MIN_SPEED
		ball.speed = self.speed

		# Rotate both balls
		self.direction.rotate(POWER_UP_DUPLICATION_BALL_DEGREES_DEVIATON)
		ball.direction.rotate(-POWER_UP_DUPLICATION_BALL_DEGREES_DEVIATON)

		# Set RUN state
		ball.state = STATE_RUN

		# Get info of last paddle touch
		ball.lastPaddleHitId = self.lastPaddleHitId

		# Dup power up effects
		if self.modifierSize != 1:
			ball.modifySize(self.modifierSize)
		ball.modifierSkipCollision = self.modifierSkipCollision
		ball.modifierInvisibleBall = self.modifierInvisibleBall
		ball.modifierInvisibleBallTimer = self.modifierInvisibleBallTimer
		ball.modifierWaveBall = self.modifierWaveBall
		ball.modifierWaveBallTimer = self.modifierWaveBallTimer

		ball.powerUpEffects = self.powerUpEffects

		ball.numberOfBounce = self.numberOfBounce

		return ball


	def addPowerUpEffect(self, powerUp):
		powerUpEffect = None

		if powerUp == POWER_UP_BALL_SLOW:
			powerUpEffect = [powerUp, POWER_UP_BALL_SLOW_TIME_EFFECT]
			self.modifierSpeed /= POWER_UP_BALL_SLOW_SPEED_FACTOR

		elif powerUp == POWER_UP_BALL_BIG:
			powerUpEffect = [powerUp, POWER_UP_BALL_BIG_TIME_EFFECT]
			self.modifierSize *= POWER_UP_BALL_BIG_SIZE_FACTOR
			self.modifySize(self.modifierSize)

		elif powerUp == POWER_UP_BALL_LITTLE:
			powerUpEffect = [powerUp, POWER_UP_BALL_LITTLE_TIME_EFFECT]
			self.modifierSize /= POWER_UP_BALL_LITTLE_SIZE_FACTOR
			self.modifySize(self.modifierSize)

		if powerUpEffect != None:
			self.powerUpEffects.append(powerUpEffect)
