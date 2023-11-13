from define import *
from pg_utils import *

import paddle

class Team:
	def __init__(self, numberOfPlayers:int, leftSide:bool) -> None:
		if numberOfPlayers < 1:
			numberOfPlayers = 1
		elif numberOfPlayers > TEAM_MAX_PLAYER:
			numberOfPlayers = TEAM_MAX_PLAYER

		self.leftSide = leftSide

		if leftSide:
			xPos = AREA_RECT[0] + AREA_BORDER_SIZE * 2
			id = 0
		else:
			xPos = AREA_RECT[0] + AREA_RECT[2] - AREA_BORDER_SIZE * 2
			id = TEAM_MAX_PLAYER

		self.paddles = []
		if numberOfPlayers == 1:
			self.paddles.append(paddle.Paddle(xPos, AREA_RECT[1] + AREA_RECT[3] // 2, id))
		else:
			self.paddles.append(paddle.Paddle(xPos, AREA_RECT[1] + AREA_RECT[3] // 3, id))
			self.paddles.append(paddle.Paddle(xPos, AREA_RECT[1] + AREA_RECT[3] // 3 * 2, id + 1))

		self.score = 0


	def tick(self, delta:float, keyboardState:list, balls:list) -> None:
		for i in range(len(self.paddles)):
			self.paddles[i].updateTimes(delta)

			# Only python client
			keyId = i
			if not self.leftSide:
				keyId += TEAM_MAX_PLAYER

			if keyboardState[PLAYER_KEYS[keyId][KEY_UP]]:
				self.paddles[i].move("up", delta)
			if keyboardState[PLAYER_KEYS[keyId][KEY_DOWN]]:
				self.paddles[i].move("down", delta)
			if keyboardState[PLAYER_KEYS[keyId][KEY_POWER_UP]]:
				#balls[0].modifierZigZagBall = True
				#balls[0].modifierSpeed = 2.5
				pass


	def draw(self, win):
		for p in self.paddles:
			p.draw(win)

		if self.leftSide:
			drawText(win, "SCORE : " + str(self.score), (AREA_MARGIN, AREA_MARGIN / 2), (255, 255, 255), size=30, align="mid-left")
		else:
			drawText(win, "SCORE : " + str(self.score), (WIN_WIDTH - AREA_MARGIN, AREA_MARGIN / 2), (255, 255, 255), size=30, align="mid-right")

