import math


def pointSub(p1, p2):
	return Point(p1.x - p2.x, p1.y - p2.y)


class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y


	def translate(self, x, y):
		self.x += x
		self.y += y


	def rotateAround(self, x, y, sinTmp, cosTmp):
		# Move point to center
		self.x -= x
		self.y -= y

		# Apply rotation
		self.x = (self.x * cosTmp) - (self.y * sinTmp)
		self.y = (self.x * sinTmp) + (self.y * cosTmp)

		# Uncenter point
		self.x += x
		self.y += y


	def asTupple(self):
		return (self.x, self.y)


	def asTuppleCenter(self, x, y):
		return (self.x - x, self.y - y)
