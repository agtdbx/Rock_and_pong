import client_side.client
import server_side.server

client = client_side.client.Client()
server = server_side.server.Server()

while client.runMainLoop:
	# Run server step for make all calculation
	server.step()

	# Give messages from server to client
	client.messageFromServer.extend(server.messageForClients)

	# Run client step to draw server change, and check user input
	client.step()

	# Give messages from client to server
	server.messageFromClients.extend(client.messageForServer)

client.quit()
