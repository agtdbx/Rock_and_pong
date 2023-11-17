from define import *
from vec2 import *
import hitbox

class Paddle:
	def	__init__(self, x, y, id, team) -> None:
		self.id = id
		self.pos = Vec2(x, y)
		self.w = PADDLE_WIDTH
		self.h = PADDLE_HEIGHT
		self.halfW = PADDLE_WIDTH / 2
		self.halfH = PADDLE_HEIGHT / 2

		self.hitbox = hitbox.Hitbox(x, y, HITBOX_PADDLE_COLOR, PADDLE_COLOR)
		self.hitbox.addPoint(-self.halfW, -self.halfH)
		self.hitbox.addPoint(self.halfW, -self.halfH)
		self.hitbox.addPoint(self.halfW, self.halfH)
		self.hitbox.addPoint(-self.halfW, self.halfH)

		self.team = team

		self.waitLaunch = 0
		self.waitUsePowerUp = 0

		self.modifierSpeed = 1
		self.modifierSize = 1

		# Represente the effect on paddle [POWER_UP, TIME_EFFECT]
		self.powerUpEffects = []

		self.powerUp = POWER_UP_NONE

		self.powerUpInCharge = []

		# For stats
		self.numberOfGoal = 0
		self.maxSpeedBallTouch = 0
		self.maxBounceBallGoal = 0
		self.numberOfContreCamp = 0
		self.numberOfPerfectShoot = 0


	def updateTimes(self, delta):
		if self.waitLaunch > 0:
			self.waitLaunch -= delta
			if self.waitLaunch < 0:
				self.waitLaunch = 0

		if self.waitUsePowerUp > 0:
			self.waitUsePowerUp -= delta
			if self.waitUsePowerUp < 0:
				self.waitUsePowerUp = 0

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
					if powerUpEffect[0] == POWER_UP_PADDLE_FAST:
						self.modifierSpeed /= POWER_UP_PADDLE_FAST_SPEED_FACTOR

					elif powerUpEffect[0] == POWER_UP_PADDLE_SLOW:
						self.modifierSpeed *= POWER_UP_PADDLE_SLOW_SPEED_FACTOR

					elif powerUpEffect[0] == POWER_UP_PADDLE_BIG:
						self.modifierSize /= POWER_UP_PADDLE_BIG_SIZE_FACTOR
						self.modifySize(self.modifierSize)

					elif powerUpEffect[0] == POWER_UP_PADDLE_LITTLE:
						self.modifierSize *= POWER_UP_PADDLE_LITTLE_SIZE_FACTOR
						self.modifySize(self.modifierSize)

		for i in range(len(powerUpEffectToRemove)):
			self.powerUpEffects.pop(powerUpEffectToRemove[i] - i)


	def move(self, dir, delta):
		if dir == "up":
			self.pos.y -= PADDLE_SPEED * self.modifierSpeed * delta
			if self.pos.y - (self.halfH * self.modifierSize) < AREA_RECT[1] + PERFECT_SHOOT_SIZE:
				self.pos.y = AREA_RECT[1] + PERFECT_SHOOT_SIZE + (self.halfH * self.modifierSize)
			self.hitbox.setPos(self.pos.dup())

		elif dir == "down":
			self.pos.y += PADDLE_SPEED * self.modifierSpeed * delta
			if self.pos.y + (self.halfH * self.modifierSize) > AREA_RECT[1] + AREA_RECT[3] - PERFECT_SHOOT_SIZE:
				self.pos.y = AREA_RECT[1] + AREA_RECT[3] - PERFECT_SHOOT_SIZE - (self.halfH * self.modifierSize)
			self.hitbox.setPos(self.pos.dup())


	def modifySize(self, modifier):
		self.modifierSize = modifier
		self.hitbox.clearPoints()
		self.hitbox.addPoint(-self.halfW, -self.halfH * self.modifierSize)
		self.hitbox.addPoint(self.halfW, -self.halfH * self.modifierSize)
		self.hitbox.addPoint(self.halfW, self.halfH * self.modifierSize)
		self.hitbox.addPoint(-self.halfW, self.halfH * self.modifierSize)

		if self.pos.y - (self.halfH * self.modifierSize) < AREA_RECT[1] + PERFECT_SHOOT_SIZE:
			self.pos.y = AREA_RECT[1] + PERFECT_SHOOT_SIZE + (self.halfH * self.modifierSize)
			self.hitbox.setPos(self.pos.dup())
		if self.pos.y + (self.halfH * self.modifierSize) > AREA_RECT[1] + AREA_RECT[3] - PERFECT_SHOOT_SIZE:
			self.pos.y = AREA_RECT[1] + AREA_RECT[3] - PERFECT_SHOOT_SIZE - (self.halfH * self.modifierSize)
			self.hitbox.setPos(self.pos.dup())

		if modifier != 1:
			self.modifierTimeEffect = 5


	def draw(self, win):
		if len(self.powerUpInCharge) > 0:
			if self.powerUpInCharge[0] == POWER_UP_BALL_FAST:
				self.hitbox.fillColor = POWER_UP_BALL_FAST_COLOR
			elif self.powerUpInCharge[0] == POWER_UP_BALL_WAVE:
				self.hitbox.fillColor = POWER_UP_BALL_WAVE_COLOR
			elif self.powerUpInCharge[0] == POWER_UP_BALL_INVISIBLE:
				self.hitbox.fillColor = POWER_UP_BALL_INVISIBLE_COLOR
		else:
			self.hitbox.fillColor = PADDLE_COLOR
		self.hitbox.drawFill(win)
		if DRAW_HITBOX:
			self.hitbox.draw(win)


	def addPowerUpEffect(self, powerUp):
		powerUpEffect = None

		if powerUp == POWER_UP_PADDLE_FAST:
			powerUpEffect = [powerUp, POWER_UP_PADDLE_FAST_TIME_EFFECT]
			self.modifierSpeed *= POWER_UP_PADDLE_FAST_SPEED_FACTOR

		elif powerUp == POWER_UP_PADDLE_SLOW:
			powerUpEffect = [powerUp, POWER_UP_PADDLE_SLOW_TIME_EFFECT]
			self.modifierSpeed /= POWER_UP_PADDLE_SLOW_SPEED_FACTOR

		elif powerUp == POWER_UP_PADDLE_BIG:
			powerUpEffect = [powerUp, POWER_UP_PADDLE_BIG_TIME_EFFECT]
			self.modifierSize *= POWER_UP_PADDLE_BIG_SIZE_FACTOR
			self.modifySize(self.modifierSize)

		elif powerUp == POWER_UP_PADDLE_LITTLE:
			powerUpEffect = [powerUp, POWER_UP_PADDLE_LITTLE_TIME_EFFECT]
			self.modifierSize /= POWER_UP_PADDLE_LITTLE_SIZE_FACTOR
			self.modifySize(self.modifierSize)

		if powerUpEffect != None:
			self.powerUpEffects.append(powerUpEffect)
