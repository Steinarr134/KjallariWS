import math, random, threading, time, socket, pickle, Queue

class LieServer:

	def __init__(self, host, port, messages, messageLock):
		self.port = port
		self.host = host
		self.isRunning = False
		self.messages = messages
		self.messageLock = messageLock

	def init(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((self.host, self.port))
		threading.Thread(target=self.listen, name="_socketlistener_").start()

	def listen(self):
		self.isRunning = True
		self.sock.listen(5)
		while self.isRunning:
			print "Server: Listening..."
			client, addr = self.sock.accept()
			threading.Thread(target = self.handleConnection, args = (client, addr)).start()

	def handleConnection(self, client, address):
		size = 1024
		while 1:
			try:
				req = client.recv(size)
				if req:
					msg = pickle.loads(req)
					print "Server: received:", msg
					# if self.msgLock.acquire(True):
					print "Server: message put in message queue"
					self.messages.put(msg)
					# self.msgLock.release()
					print "Server: message socket closing"
				else:
					raise error('Server: client has disconnected')		
			except:
				client.close()
				return False

	def close(self):
		self.isRunning = False
		socket.socket(socket.AF_INET, 
                  socket.SOCK_STREAM).connect((self.host, self.port))

# HOST=''
# PORT=1337
# lock = threading.Lock()
# messages = Queue.Queue()

# server = LieServer(HOST, PORT, messages, lock)
# server.init()