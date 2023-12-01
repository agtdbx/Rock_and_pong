from multiprocessing import Process
import socket
import time

def client():
	host = socket.gethostname()  # get local machine name
	port = 8080  # Make sure it's within the > 1024 $$ <65535 range

	print("Start client")
	s = socket.socket()
	s.connect((host, port))

	message = input('-> ')
	while message != 'q':
		s.send(message.encode('utf-8'))
		data = s.recv(1024).decode('utf-8')
		print('Received from server: ' + data)
		message = input('==> ')
	s.close()

def server():
	host = socket.gethostname()   # get local machine name
	port = 8080  # Make sure it's within the > 1024 $$ <65535 range

	s = socket.socket()
	s.bind((host, port))

	print("Start server")
	s.listen(1)
	client_socket, adress = s.accept()
	print("Connection from: " + str(adress))
	while True:
		data = client_socket.recv(1024).decode('utf-8')
		if not data:
			break
		print('From online user: ' + data)
		data = data.upper()
		client_socket.send(data.encode('utf-8'))
	client_socket.close()

p = Process(target=server)
p.start()
time.sleep(2)
client()
p.join()
