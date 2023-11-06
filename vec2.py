import math

class Vec2:
	def __init__(self, x, y) -> None:
		self.x = x
		self.y = y


	def __str__(self) -> str:
		return "<vec2:{x:+.2f},{y:+.2f}>".format(x=self.x, y=self.y)


	def add(self, vec) -> None:
		self.x += vec.x
		self.y += vec.y


	def subBy(self, vec) -> None:
		self.x -= vec.x
		self.y -= vec.y


	def multiply(self, nb) -> None:
		self.x *= nb
		self.y *= nb


	def divide(self, nb) -> None:
		if nb == 0:
			return
		self.x /= nb
		self.y /= nb


	def translate(self, x, y) -> None:
		self.x += x
		self.y += y


	def translateAlong(self, vec, dist) -> None:
		self.x += vec.x * dist
		self.y += vec.y * dist


	def rotateAround(self, x, y, sinTmp, cosTmp) -> None:
		# Move point to center
		self.x -= x
		self.y -= y

		# Apply rotation
		self.x = (self.x * cosTmp) - (self.y * sinTmp)
		self.y = (self.x * sinTmp) + (self.y * cosTmp)

		# Uncenter point
		self.x += x
		self.y += y


	def asTupple(self) -> tuple:
		return (self.x, self.y)


	def asTuppleCenter(self, x, y) -> tuple:
		return (self.x - x, self.y - y)


	def norm(self) -> float:
		return math.sqrt(self.x**2 + self.y**2)


	def normalize(self) -> None:
		norm = self.norm()
		if norm != 0:
			self.x /= norm
			self.y /= norm


	def rotate(self, angle) -> None:
		rad = angle * (math.pi / 180)
		cosRad = math.cos(rad)
		sinRad = math.sin(rad)

		self.x = self.x * cosRad - self.y * sinRad
		self.y = self.y * sinRad + self.y * cosRad


	def dup(self) -> None:
		return Vec2(self.x, self.y)



def vec2Add(vec1, vec2) -> Vec2:
	return Vec2(vec1.x + vec2.x, vec1.y + vec2.y)


def vec2Sub(vec1, vec2) -> Vec2:
	return Vec2(vec1.x - vec2.x, vec1.y - vec2.y)


def vec2Dot(vec1, vec2) -> int:
	return (vec1.x * vec2.x) + (vec1.y * vec2.y)


def vec2Cross(vec1, vec2) -> int:
	return (vec1.x * vec2.y) - (vec1.y * vec2.x)


def getNormalOfSegment(vec1, vec2) -> Vec2:
	dx = vec2.x - vec1.x
	dy = vec2.y - vec1.y
	vec = Vec2(-dy, dx)
	vec.normalize()
	return vec


# def vec2AngleBeetween(vec1, vec2) -> int:
# 	return vec1.x * vec2.x + vec1.y * vec2.y


def reflectionAlongVec2(normal, vec) -> Vec2:
	dot = vec2Dot(normal, vec)
	if (dot >= 0):
		normal.multiply(-1)

	vecProjOnNormal = normal.dup()
	vecProjOnNormal.multiply(vec2Dot(vec, normal) / vec2Dot(vec, vec))

	vecProjOnNormal.multiply(2)
	reflectedVec = vec2Sub(vec, vecProjOnNormal)

	reflectedVec.normalize()

	# angle = vec2AngleBeetween(normal, vec)
	# print("Angle", angle)

	# vec.rotate(-2 * angle)

	# vec.normalize()

	return reflectedVec
