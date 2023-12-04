import select
import socket
import sys

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 20000  # The port used by the server

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((HOST, PORT))

pollerObject = select.poll()
pollerObject.register(0, select.POLLIN)
pollerObject.register(clientSocket, select.POLLIN)

runClient = True

while(runClient):
    fdVsEvent = pollerObject.poll(10000)
    for descriptor, Event in fdVsEvent:
        if descriptor == 0:
            # Read line from stdin
            msg = sys.stdin.readline()
            # Remove \n
            msg = msg[:-1]
            if msg == "q":
                print("/!\\ CLIENT EXIT /!\\")
                runClient = False
            else:
                print("Stdin input :", msg)
                clientSocket.sendall(bytes(msg, encoding='utf-8'))
            continue
        elif descriptor == clientSocket.fileno():
            msg = clientSocket.recv(1024).decode('utf-8')
            if not msg:
                print("Server close")
                runClient = False
                break
            print("Message from server :", msg)
            continue
        print("WTF t'es qui toi")

    if len(fdVsEvent) == 0:
        print("Nothing recieved")
