import pygame as pg

def drawText(surface, text, pos, color=(0, 0, 0), size=24, font=None, align="left"):
	font = pg.font.SysFont(font, size)
	img = font.render(text, True, color)

	if align == "top-left":
		placement = pos
	elif align == "mid-left":
		placement = (pos[0], pos[1] - img.get_height() / 2)
	elif align == "bot-left":
		placement = (pos[0], pos[1] - img.get_height())

	elif align == "top-center":
		placement = (pos[0] - img.get_width() / 2, pos[1])
	elif align == "mid-center":
		placement = (pos[0] - img.get_width() / 2, pos[1] - img.get_height() / 2)
	elif align == "bot-center":
		placement = (pos[0] - img.get_width() / 2, pos[1] - img.get_height())

	elif align == "top-right":
		placement = (pos[0] - img.get_width(), pos[1])
	elif align == "mid-right":
		placement = (pos[0] - img.get_width(), pos[1] - img.get_height() / 2)
	elif align == "bot-right":
		placement = (pos[0] - img.get_width(), pos[1] - img.get_height())

	surface.blit(img, placement)
