import client_side.client
import server_side.server

import time

server = server_side.server.Server(powerUpEnable=True)
client = client_side.client.Client()

# Give messages from server to client
client.messageFromServer.extend(server.messageForClients)

checkTime = []

while server.runMainLoop and client.runMainLoop:
	beforeLoop = time.time()
	before = beforeLoop
	# Run server step for make all calculation
	server.step()
	timeServerTick = time.time() - before

	# Give messages from server to client
	client.messageFromServer.extend(server.messageForClients)

	before = time.time()
	# Run client step to draw server change, and check user input
	client.step()
	timeClientTick = time.time() - before

	# Give messages from client to server
	server.messageFromClients.extend(client.messageForServer)
	checkTime.append((timeServerTick, timeClientTick, time.time() - beforeLoop))

client.quit()
server.printFinalStat()

minServerTick = 10
moyServerTick = 0
maxServerTick = 0
minClientTick = 10
moyClientTick = 0
maxClientTick = 0
minLoopTick = 10
moyLoopTick = 0
maxLoopTick = 0

for ser, cli, loop in checkTime:
	if ser < minServerTick:
		minServerTick = ser
	if ser > maxServerTick:
		maxServerTick = ser
	moyServerTick += ser

	if cli < minClientTick:
		minClientTick = ser
	if cli > maxClientTick:
		maxClientTick = ser
	moyClientTick += ser

	if loop < moyLoopTick:
		moyLoopTick = ser
	if loop > maxLoopTick:
		maxLoopTick = ser
	moyLoopTick += ser

moyServerTick /= len(checkTime)
moyClientTick /= len(checkTime)
moyLoopTick /= len(checkTime)

print("Server performance :")
print("\tMinimum fps : ", 1 / minServerTick, " (", minServerTick, ")", sep="")
print("\tAverage fps : ", 1 / moyServerTick, " (", moyServerTick, ")", sep="")
print("\tMaximum fps : ", 1 / maxServerTick, " (", maxServerTick, ")", sep="")
print("Client performance :")
print("\tMinimum fps : ", 1 / minClientTick, " (", minClientTick, ")", sep="")
print("\tAverage fps : ", 1 / moyClientTick, " (", moyClientTick, ")", sep="")
print("\tMaximum fps : ", 1 / maxClientTick, " (", maxClientTick, ")", sep="")
print("Loop performance :")
print("\tMinimum fps : ", 1 / minLoopTick, " (", minLoopTick, ")", sep="")
print("\tAverage fps : ", 1 / moyLoopTick, " (", moyLoopTick, ")", sep="")
print("\tMaximum fps : ", 1 / maxLoopTick, " (", maxLoopTick, ")", sep="")
