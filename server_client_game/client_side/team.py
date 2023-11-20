from client_side.client_define import *
from client_side.pg_utils import *
import client_side.paddle as paddle

class Team:
	def __init__(self, numberOfPlayers:int, team:int) -> None:
		if numberOfPlayers < 1:
			numberOfPlayers = 1
		elif numberOfPlayers > TEAM_MAX_PLAYER:
			numberOfPlayers = TEAM_MAX_PLAYER

		self.team = team

		if self.team == TEAM_LEFT:
			xPos = AREA_RECT[0] + AREA_BORDER_SIZE * 2
		else:
			xPos = AREA_RECT[0] + AREA_RECT[2] - AREA_BORDER_SIZE * 2

		self.paddles = []
		if numberOfPlayers == 1:
			self.paddles.append(paddle.Paddle(xPos, AREA_RECT[1] + AREA_RECT[3] // 2, 0, self.team))
		else:
			self.paddles.append(paddle.Paddle(xPos, AREA_RECT[1] + AREA_RECT[3] // 3, 0, self.team))
			self.paddles.append(paddle.Paddle(xPos, AREA_RECT[1] + AREA_RECT[3] // 3 * 2, 1, self.team))

		self.score = 0
		# list of power up who try to use : [power up id, paddle id, power up used (bool)]
		self.powerUpTryUse = []


	def tick(self, delta:float, paddlesKeyState:list, updateTime:bool) -> None:
		# Check input
		for i in range(len(self.paddles)):
			if updateTime:
				self.paddles[i].updateTimes(delta)

			keyId = i
			if self.team == TEAM_RIGHT:
				keyId += TEAM_MAX_PLAYER

			if paddlesKeyState[keyId * 4 + KEY_UP]:
				self.paddles[i].move("up", delta)
			if paddlesKeyState[keyId * 4 + KEY_DOWN]:
				self.paddles[i].move("down", delta)


	def draw(self, win):
		for p in self.paddles:
			p.draw(win)

		if self.team == TEAM_LEFT:
			drawText(win, "SCORE : " + str(self.score), (75, 75 / 2), (255, 255, 255), size=30, align="mid-left")

			drawText(win, str(self.paddles[0].powerUp), (75, 70), (255, 255, 255), size=30, align="mid-right")
			if len(self.paddles) == 2:
				drawText(win, str(self.paddles[1].powerUp), (75, WIN_HEIGHT - 70), (255, 255, 255), size=30, align="mid-right")


		else:
			drawText(win, "SCORE : " + str(self.score), (WIN_WIDTH - 75, 75 / 2), (255, 255, 255), size=30, align="mid-right")

			drawText(win, str(self.paddles[0].powerUp), (WIN_WIDTH - 75, 70), (255, 255, 255), size=30, align="mid-left")
			if len(self.paddles) == 2:
				drawText(win, str(self.paddles[1].powerUp), (WIN_WIDTH - 75, WIN_HEIGHT - 70), (255, 255, 255), size=30, align="mid-left")


	def applyPowerUpToPaddles(self, powerUp):
		for p in self.paddles:
			p.addPowerUpEffect(powerUp)
