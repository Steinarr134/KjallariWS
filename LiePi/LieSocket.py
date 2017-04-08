import math, random, threading, time, socket, pickle, Queue

class LieSocket:

	def __init__(self, host, port, messages, messageLock):
		self.host = host
		self.port = port
		self.isRunning = False
		self.messages = messages
		self.messageLock = messageLock

	def init(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		threading.Thread(target=self.connect_with_retry, name="_socketlistener_").start()

	def connect_with_retry(self):
		# Handle retries if connection fails
		print "Client: Connecting with retry:"
		# while True:
		try:
			self.connect()
			self.send("Hello from client!")
		except Exception as e:
			time.sleep(1)
			print(type(e))
			print(e.args)
			print(e)

	def send(self, payload):
		self.sock.send(pickle.dumps(payload))
		print "Client: message sent"

	def connect(self):
		print "Client: Trying to connect..."
		self.sock.connect((self.host, self.port))
		print "Client: connected."

	def handleIncoming(self, client, address):
		size = 1024
		while 1:
			try:
				req = client.recv(size)
				if req:
					msg = pickle.loads(req)
					print "received:", msg
					if self.msgLock.acquire(True):
						print "message put in message queue"
						self.messages.put(msg)
						self.msgLock.release()
					print "message socket closing"
				else:
					raise error('client disconnected')		
			except:
				client.close()
				return False

	def close(self):
		pass




# class LieSocket:

# 	def __init__(self, host, port, messages, messageLock):
# 		self.port = port
# 		self.host = host
# 		self.isRunning = False
# 		self.messages = messages
# 		self.messageLock = messageLock

# 	def init(self):
# 		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 		self.sock.bind((self.host, self.port))
# 		threading.Thread(target=self.listen, name="_socketlistener_").start()

# 	def listen(self):
# 		self.isRunning = True
# 		self.sock.listen(5)
# 		while self.isRunning:
# 			print "Listening..."
# 			client, addr = self.sock.accept()
# 			threading.Thread(target = self.handleConnection, args = (client, addr)).start()

# 	def handleConnection(self, client, address):
# 		size = 1024
# 		while 1:
# 			try:
# 				req = client.recv(size)
# 				if req:
# 					msg = pickle.loads(req)
# 					print "received:", msg
# 					if self.msgLock.acquire(True):
# 						print "message put in message queue"
# 						self.messages.put(msg)
# 						self.msgLock.release()
# 					print "message socket closing"
# 				else:
# 					raise error('client disconnected')		
# 			except:
# 				client.close()
# 				return False

# 	def close(self):
# 		self.isRunning = False
# 		socket.socket(socket.AF_INET, 
#                   socket.SOCK_STREAM).connect((HOST, PORT))
