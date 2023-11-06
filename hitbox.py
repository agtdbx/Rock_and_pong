import point

import pygame as pg
import math


def collideBetweenSegments(p0, p1, p2, p3):
	s1 = point.pointSub(p1, p0)
	s2 = point.pointSub(p3, p2)

	p0_minus_p2 = point.pointSub(p0, p2)

	divisor = -s2.x * s1.y + s1.x - s2.y

	if divisor == 0:
		return False

	s = (-s1.y * p0_minus_p2.x + s1.x * p0_minus_p2.y) / divisor

	if s < 0 or 1 < s:
		return False

	t = ( s2.x * p0_minus_p2.y - s2.y * p0_minus_p2.x) / divisor

	if t < 0 or 1 < t:
		return False

	return True


class Hitbox:
	def __init__(self, x, y, color):
		self.x = x
		self.y = y

		self.color = color

		self.rect = [0, 0, 0, 0]

		self.rotation = 0

		self.points = []


	def __str__(self):
		return "<hitbox:" + str(self.x) + ", " + str(self.y) + "| " + str(len(self.points)) + " points >"


	def addPoint(self, x, y):
		self.points.append(point.Point(self.x + x, self.y + y))
		self.computeSurroundingRect()


	def computeSurroundingRect(self):
		if len(self.points) == 0:
			return

		pos = self.points[0].asTuppleCenter(self.x, self.y)

		xLeft = pos[0]
		xRight = pos[0]
		yUp = pos[1]
		yDown = pos[1]

		for i in range (1, len(self.points)):
			pos = self.points[i].asTuppleCenter(self.x, self.y)

			if (pos[0] < xLeft):
				xLeft = pos[0]
			elif (pos[0] > xRight):
				xRight = pos[0]

			if (pos[1] < yUp):
				yUp = pos[1]
			elif (pos[1] > yDown):
				yDown = pos[1]

		self.rect[0] = xLeft + self.x
		self.rect[2] = xRight - xLeft + 1
		self.rect[1] = yUp + self.y
		self.rect[3] = yDown - yUp + 1


	def setPos(self, x, y):
		dx = x - self.x
		dy = y - self.y
		self.x = x
		self.y = y
		for i in range (len(self.points)):
			self.points[i].translate(dx, dy)
		self.computeSurroundingRect()



	def move(self, x, y):
		self.x += x
		self.y += y
		for i in range (len(self.points)):
			self.points[i].translate(x, y)
		self.computeSurroundingRect()


	def rotate(self, degrees):
		self.rotation += degrees

		radiant = degrees * (math.pi / 180)
		sinTmp = math.sin(radiant)
		cosTmp = math.cos(radiant)

		for i in range (len(self.points)):
			self.points[i].rotateAround(self.x, self.y, sinTmp, cosTmp)
		self.computeSurroundingRect()


	def draw(self, win):
		for i in range (0, len(self.points)):
			pg.draw.line(win, self.color, self.points[i - 1].asTupple(), self.points[i].asTupple())

		# if (len(self.points) > 1):
		# 	pg.draw.rect(win, (0, 0, 255), self.rect, 1)



	def isCollide(self, hitbox):
		pointsSize = len(self.points)
		if (pointsSize <= 1):
			return False

		hitboxPointsSize = len(hitbox.points)
		if (hitboxPointsSize <= 1):
			return False

		if self.rect[0] + self.rect[2] >= hitbox.rect[0] and self.rect[0] <= hitbox.rect[0] + hitbox.rect[2] and \
			self.rect[1] + self.rect[3] >= hitbox.rect[1] and self.rect[1] <= hitbox.rect[1] + hitbox.rect[3]:

			for i in range (0, pointsSize):
				p0 = self.points[i - 1]
				p1 = self.points[i]

				for j in range (0, hitboxPointsSize):
					p2 = hitbox.points[j - 1]
					p3 = hitbox.points[j]

					if collideBetweenSegments(p0, p1, p2, p3):
						return True

		return False
