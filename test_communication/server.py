import select
import socket
import sys

serverSocket    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ipAddress   = '127.0.0.1'
portNumber  = 20000

serverSocket.bind((ipAddress, portNumber))
serverSocket.listen()

pollerObject = select.poll()
pollerObject.register(0, select.POLLIN)
pollerObject.register(serverSocket, select.POLLIN)

clientSockets = []

runServer = True

while(runServer):
    fdVsEvent = pollerObject.poll(16)
    for descriptor, Event in fdVsEvent:
        if descriptor == 0:
            # Read line from stdin
            msg = sys.stdin.readline()
            # Remove \n
            msg = msg[:-1]
            if msg == "q":
                print("/!\\ SERVER EXIT /!\\")
                runServer = False
            else:
                print("Stdin input :", msg)
                for clientSocket in clientSockets:
                    clientSocket.sendall(bytes(msg, encoding='utf-8'))
            continue
        elif descriptor == serverSocket.fileno():
            conn, addr = serverSocket.accept()
            print("Client", len(clientSockets), "added")
            pollerObject.register(conn, select.POLLIN)
            clientSockets.append(conn)
            conn.sendall(b"Welcom to hell")
            continue
        for i in range(len(clientSockets)):
            if descriptor == clientSockets[i].fileno():
                msg = clientSockets[i].recv(1024).decode('utf-8')
                if not msg:
                    print("Client", i, "disconnected")
                    pollerObject.unregister(clientSockets[i])
                else:
                    if len(msg) > 5 and msg[:5] == "DATA:":
                        data = msg[5:]
                        data = eval(data)
                        print(data["test"])
                        print(data)
                    print("Client", i, ":", msg)

    # if len(fdVsEvent) == 0:
    #     print("Nothing recieved")
