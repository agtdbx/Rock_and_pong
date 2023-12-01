from define import *
import client_side.client as client
import server_side.server as server


map_to_load = 2
paddles_left = [PADDLE_PLAYER]
paddles_right = [PADDLE_IA]
powerUpEnable=True

server = server.Server(
			powerUpEnable, paddles_left, paddles_right, map_to_load)
client = client.Client()

# Give messages from server to client
client.messageFromServer.extend(server.messageForClients)

checkTime = []

while server.runMainLoop and client.runMainLoop:
	# Run server step for make all calculation
	server.step()

	# Give messages from server to client
	client.messageFromServer.extend(server.messageForClients)

	# Run client step to draw server change, and check user input
	client.step()

	# Give messages from client to server
	server.messageFromClients.extend(client.messageForServer)

client.quit()
server.printFinalStat()
