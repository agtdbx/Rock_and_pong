import client_side.client
import server_side.server

server = server_side.server.Server(powerUpEnable=False)
client = client_side.client.Client()

# Give messages from server to client
client.messageFromServer.extend(server.messageForClients)

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
