import threading, time, socket, pickle, Queue
from Server import LieServer
from LieSocket import LieSocket

SERVER_HOST ='localhost'
SERVER_PORT =13370
serverLock = threading.Lock()
serverMessages = Queue.Queue()
clientLock = threading.Lock()
clientMessages = Queue.Queue()

def start_server():
	server = LieServer(SERVER_HOST, SERVER_PORT , serverMessages, serverLock)
	server.init()
	time.sleep(2)
	server.close()

def start_client():
	# CLIENT_HOST ='localhost'
	# CLIENT_PORT =13380
	client = LieSocket(SERVER_HOST, SERVER_PORT, clientLock, clientMessages)
	client.init()
	# time.sleep(1)

threading.Thread(target = start_server).start()
time.sleep(1)
threading.Thread(target = start_client).start()

print serverMessages.get()

# client.close()

time.sleep(2)