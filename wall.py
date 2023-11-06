from define import *
from vec2 import *
import hitbox

import pygame as pg


class Wall:
	def __init__(self, x, y, w, h, color) -> None:
		self.pos = Vec2(x, y)
		self.w = w
		self.h = h
		self.halfW = w / 2
		self.halfH = h / 2

		self.hitbox = hitbox.Hitbox(self.pos.x, self.pos.y, HITBOX_WALL_COLOR, color)
		self.hitbox.addPoint(-self.halfW, -self.halfH)
		self.hitbox.addPoint(self.halfW, -self.halfH)
		self.hitbox.addPoint(self.halfW, self.halfH)
		self.hitbox.addPoint(-self.halfW, self.halfH)


	def translate(self, vec):
		self.pos.add(vec)
		self.hitbox.move(vec.x, vec.y)


	def rotate(self, angle):
		self.hitbox.rotate(angle)


	def draw(self, win):
		self.hitbox.drawFill(win)
		self.hitbox.draw(win)


	def makeCollisionWithBall(self, ball):
		if not self.hitbox.isCollide(ball.hitbox):
			return

		collideInfos = self.hitbox.getCollideInfo(ball.hitbox)

		print("\nCollideInfos")
		for collideInfo in collideInfos:
			if collideInfo[0]:
				print(collideInfo[1], collideInfo[2], collideInfo[3])

				touchPos = collideInfo[1]
				p0 = collideInfo[2]
				p1 = collideInfo[3]
				normal = getNormalOfSegment(p0, p1)
				print("Normal", ball.direction)
				print("Dir", ball.direction)
				ball.direction = reflectionAlongVec2(normal, ball.direction)
				print("Dir", ball.direction)
				break

		# distToTravel =
