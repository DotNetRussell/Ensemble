#!/usr/bin/python3

import socket
import threading 
import ensemble_logging

EMPTY_BYTES = bytes("".encode())
END_MARKER = bytes("%%END_=_MARKER%%".encode())

def remove_end_marker(data):
	return data.replace(END_MARKER,EMPTY_BYTES)

def txrx(ip,port,message):
	if(ip == None or port == None or message == None):
		ensemble_logging.log_message(f"TXRX exception\r\nip:{ip}\r\nport:{port}\r\nmessage: {message}")
		return None

	responseBuffer = ""
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(10)
		sock.connect((ip, port))

		message += END_MARKER
		sock.send(message)

		responseBuffer = EMPTY_BYTES
		while True:
			try:
				responseBuffer += sock.recv(1024)
				if(END_MARKER in responseBuffer):
					responseBuffer = remove_end_marker(responseBuffer)		
					break			
				elif len(responseBuffer) == 0:
					ensemble_logging.log_message("Empty response recieved from agent")					
					break
			except Exception as error:
				ensemble_logging.log_message(f"Incomming message exception\r\nip:{ip} port:{port}\r\n{error}")
				break
	except Exception as error:
		ensemble_logging.log_message(f"Incomming message exception\r\nip:{ip} port:{port}\r\n{error}")
	return responseBuffer

def tx(ip,port,message):
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip, port))

		message += END_MARKER
		sock.send(message)
	except:
		ensemble_logging.log_message(f"Connection failed {ip}:{port}")
		return

def start_server(bindIp, bindPort, callback):
	ensemble_logging.log_message(f"Starting server binding to {bindIp}:{bindPort}")
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serverSocket.bind((bindIp, int(bindPort)))
	serverSocket.listen(100)

	while True:
		try:
			connection, address = serverSocket.accept()
			request = connection.recv(1024)
			ensemble_logging.log_message(f"Message Received {connection} {address} {request}")
			threading.Thread(target=callback,args=(request,address,))
		except:
			ensemble_logging.log_message("Issue with incoming message")


