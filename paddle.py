from define import *
from vec2 import *
import hitbox

import pygame as pg


class Paddle:
	def	__init__(self, x, y, id) -> None:
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

		self.waitLaunch = 0


	def move(self, dir, delta):
		if dir == "up":
			self.pos.y -= PADDLE_SPEED * delta
			if self.pos.y - self.halfH < AREA_RECT[1] + PERFECT_SHOOT_SIZE:
				self.pos.y = AREA_RECT[1] + PERFECT_SHOOT_SIZE + self.halfH
			self.hitbox.setPos(self.pos.dup())

		elif dir == "down":
			self.pos.y += PADDLE_SPEED * delta
			if self.pos.y + self.halfH > AREA_RECT[1] + AREA_RECT[3] - PERFECT_SHOOT_SIZE:
				self.pos.y = AREA_RECT[1] + AREA_RECT[3] - PERFECT_SHOOT_SIZE - self.halfH
			self.hitbox.setPos(self.pos.dup())


	def draw(self, win):
		self.hitbox.drawFill(win)
