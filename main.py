from define import *
from pg_utils import *
from vec2 import *
import ball
import hitbox

import pygame as pg
import math
import time
import sys


def createWall(x, y, w, h, color) -> hitbox.Hitbox:
	halfW = w / 2
	halfH = h / 2

	hit = hitbox.Hitbox(x, y, HITBOX_WALL_COLOR, color)
	hit.addPoint(-halfW, -halfH)
	hit.addPoint(halfW, -halfH)
	hit.addPoint(halfW, halfH)
	hit.addPoint(-halfW, halfH)

	return hit


def createObstacle(x:int, y:int, listPoint:list, color:tuple) -> hitbox.Hitbox:
	hit = hitbox.Hitbox(x, y, HITBOX_WALL_COLOR, color)

	for p in listPoint:
		hit.addPoint(p[0], p[1])

	return hit


class Game:
	def __init__(self):
		"""
		This method define all variables needed by the program
		"""
		# Start of pygame
		pg.init()

		# We remove the toolbar of the window's height
		self.winSize = ((WIN_WIDTH, WIN_HEIGHT))
		# We create the window
		self.win = pg.display.set_mode(self.winSize, pg.RESIZABLE)

		self.clock = pg.time.Clock() # The clock be used to limit our fps
		self.fps = 60

		self.last = time.time()

		self.runMainLoop = True

		# Ball creation
		self.ball = ball.Ball(AREA_BORDER_RECT[0] + AREA_BORDER_RECT[2] / 2, AREA_BORDER_RECT[1] + AREA_BORDER_RECT[3] / 2)

		# Walls creation
		self.walls = [
			# Wall up
			createWall(
				AREA_BORDER_RECT[0] + AREA_BORDER_RECT[2] / 2,
			 	AREA_BORDER_RECT[1] + AREA_BORDER_SIZE / 2,
				AREA_BORDER_RECT[2],
				AREA_BORDER_SIZE,
				(50, 50, 50)
			),
			# Wall down
			createWall(
				AREA_BORDER_RECT[0] + AREA_BORDER_RECT[2] / 2,
				AREA_BORDER_RECT[1] + AREA_BORDER_RECT[3] - AREA_BORDER_SIZE / 2,
				AREA_BORDER_RECT[2],
				AREA_BORDER_SIZE,
				(50, 50, 50)
			),
			# Obstable
			createObstacle(
				AREA_BORDER_RECT[0] + AREA_BORDER_RECT[2] / 2,
				AREA_BORDER_RECT[1] + AREA_BORDER_RECT[3] / 4,
				[(-70, -70), (0, -100), (70, -70), (100, 0), (70, 70), (0, 100), (-70, 70), (-100, 0)],
				(150, 150, 0)
			)
		]

		# Scores
		self.player1Score = 0
		self.player2Score = 0


	def run(self):
		"""
		This method is the main loop of the game
		"""
		# Game loop
		while self.runMainLoop:
			self.input()
			self.tick()
			self.render()
			self.clock.tick(self.fps)


	def input(self):
		"""
		The method catch user's inputs, as key presse or a mouse click
		"""
		# We check each event
		for event in pg.event.get():
			# If the event it a click on the top right cross, we quit the game
			if event.type == pg.QUIT:
				self.quit()

		self.keyboardState = pg.key.get_pressed()
		self.mouseState = pg.mouse.get_pressed()
		self.mousePos = pg.mouse.get_pos()

		# Press espace to quit
		if self.keyboardState[pg.K_ESCAPE]:
			self.quit()


	def tick(self):
		"""
		This is the method where all calculations will be done
		"""
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		if self.mouseState[0]:
			self.ball.affecteDirection(self.mousePos)

		self.ball.updatePosition(delta, self.walls)

		if self.ball.inWaiting:
			if self.ball.pos.x < WIN_WIDTH / 2:
				self.player2Score += 1
			else:
				self.player1Score += 1
			self.ball.speed = 0
			self.ball.pos.x = AREA_BORDER_RECT[0] + AREA_BORDER_RECT[2] / 2
			self.ball.pos.y = AREA_BORDER_RECT[1] + AREA_BORDER_RECT[3] / 2
			self.ball.inWaiting = False


		pg.display.set_caption(str(self.clock.get_fps()))


	def render(self):
		"""
		This is the method where all graphic update will be done
		"""
		# We clean our screen with one color
		self.win.fill((0, 0, 0))

		# Draw area
		pg.draw.rect(self.win, AREA_BORDER_COLOR, AREA_BORDER_RECT, AREA_BORDER_SIZE)
		pg.draw.rect(self.win, AREA_COLOR, AREA_RECT)

		# Draw ball
		for w in self.walls:
			w.drawFill(self.win)

		# Draw ball
		self.ball.draw(self.win)

		# Draw score
		drawText(self.win, "Player 1 : " + str(self.player1Score), (AREA_MARGIN, AREA_MARGIN / 2), (255, 255, 255), size=30, align="mid-left")
		drawText(self.win, "Player 2 : " + str(self.player2Score), (WIN_WIDTH - AREA_MARGIN, AREA_MARGIN / 2), (255, 255, 255), size=30, align="mid-right")

		# We update the drawing.
		# Before the function call, any changes will be not visible
		pg.display.update()


	def quit(self):
		"""
		This is the quit method
		"""
		# Pygame quit
		pg.quit()
		sys.exit()


Game().run() # Start game
