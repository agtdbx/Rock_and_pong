from define import *
import client_side.game_client as game_client
import server_side.game_server as game_server


map_to_load = 2
paddles_left = [PADDLE_PLAYER]
paddles_right = [PADDLE_IA]
powerUpEnable=True

gameServer = game_server.GameServer(
			powerUpEnable, paddles_left, paddles_right, map_to_load)
gameClient = game_client.GameClient()

# Give messages from server to client
gameClient.messageFromServer.extend(gameServer.messageForClients)

checkTime = []

while gameServer.runMainLoop and gameClient.runMainLoop:
	# Run server step for make all calculation
	gameServer.step()

	# Give messages from server to client
	gameClient.messageFromServer.extend(gameServer.messageForClients)

	# Run client step to draw server change, and check user input
	gameClient.step()

	# Give messages from client to server
	gameServer.messageFromClients.extend(gameClient.messageForServer)

gameClient.quit()
gameServer.printFinalStat()
