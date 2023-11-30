from define import *
import client_side.client
import server_side.server


map_to_load = 0
paddles_left = [PADDLE_PLAYER]
paddles_right = [PADDLE_IA]
powerUpEnable=True

# {obstacle_type, obstacle_position, obstacle_color, obstacle_info, obstacle_routine}
# OBSTACLE_TYPE_RECTANGLE = 0
# OBSTACLE_TYPE_POLYGON = 1
# OBSTACLE_TYPE_CIRCLE = 2
# obstacle_info RECTANGLE : [w, h]
# obstacle_info POLYGON : [(x, y), (x, y), ...]
# obstacle_info CIRCLE : [radius, precision]
map = []

# Wall top
map.append(
	{"obstacle_type" : OBSTACLE_TYPE_RECTANGLE,
	"obstacle_position" : (AREA_SIZE[0] / 2, AREA_BORDER_SIZE / 2),
	"obstacle_color" : (50, 50, 50),
	"obstacle_info" : (AREA_SIZE[0], AREA_BORDER_SIZE * 2)}
)
# Wall bot
map.append(
	{"obstacle_type" : OBSTACLE_TYPE_RECTANGLE,
	"obstacle_position" : (AREA_SIZE[0] / 2, AREA_SIZE[1] - AREA_BORDER_SIZE / 2),
	"obstacle_color" : (50, 50, 50),
	"obstacle_info" : (AREA_SIZE[0], AREA_BORDER_SIZE * 2)}
)

if map_to_load == 1:
	pass

server = server_side.server.Server(
			powerUpEnable, paddles_left, paddles_right)
client = client_side.client.Client()

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
