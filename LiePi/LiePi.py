import Tkinter as tk
import math, random, threading, time, socket, pickle, Queue
from multiprocessing import Process, Queue as pQueue
from LieSocket import LieSocket
from HandSensor import HandSensor
from Buttons import Buttons

HOST = ''
# HOST = socket.gethostname()
PORT = 1337
SERV="192.168.1.101" # IP of the Pope
# export DISPLAY=:0.0
# xhost +ip / xhost +
# pkill -9 python


class LieGraph:

	root = None
	drawingIsRunning = False
	w = 1000
	h = 200
	bg = "#FFF"
	lineColor = "#000"
	y = 0.0
	x = 0
	MIN_DECAY = 0.15
	MAX_DECAY = 0.4
	MIN_STEP_SIZE = 0.008
	MAX_STEP_SIZE = 0.15 
	ddecay = math.pow(MIN_DECAY/MAX_DECAY, 1./10)
	dstep_size = math.pow(MIN_STEP_SIZE/MAX_STEP_SIZE, 1./10)
	t = 0
	decay = MAX_DECAY
	stepSize = MIN_STEP_SIZE
	density = 0.8
	callbackDelay = 6
	timeSinceLie = time.time()
	messages = Queue.Queue()
	msgLock = threading.Lock()
	loopCount = 0

	def __init__(self, root):
		self.root = root
		root.attributes("-fullscreen", True)
		self.messageManager = LieSocket(SERV, PORT, self.messages, self.msgLock)
		self.messageManager.init() 
		self.hand = HandSensor()
		self.hand.init()
		self.buttons = Process(target=Buttons)
		self.buttons.start()
		# self.buttons = threading.Thread(target=Buttons, name="_buttons_")
		# self.buttons.start()
		def later():
			# print "width = {}, height = {}".format(self.root.winfo_width(), self.root.winfo_height())
			self.w = self.root.winfo_width()
			self.h = self.root.winfo_height()
			self.canvas = self.createCanvasAndImage(root)
			self.canvas.pack()
			self.resetDrawing()
			self.startDrawing()
			self.root.after(self.callbackDelay, self.mainLoop)
		self.root.after(30, later)

	def createCanvasAndImage(self, frame):
		self.top = 2
		canvas = tk.Canvas(frame, width=self.w, height=self.h, bg=self.bg, highlightthickness=0)
		canvas.p = tk.PhotoImage(width=2*self.w, height=self.h)
		self.image = canvas.create_image(0, self.top, image=canvas.p, anchor=tk.NW)
		return canvas

	def mainLoop(self):
		if self.drawingIsRunning:
			self.scrollGraph(self.canvas.p)
			self.y = (1.0-self.decay)*self.y + self.stepSize*(random.random() - 0.5)
			self.drawStrip(self.canvas.p, self.y+0.5)
		self.handleMsgs()
		self.loopCount += 1
		if self.loopCount % 25 == 0:
			handPresent, lying = self.hand.isPresent()
			if lying:
				self.lie()
			self.adjustDrawParameters(handPresent)
			self.loopCount = 0
		# i = random.random()
		# drawsCount = 3
		# while self.density > i and drawsCount>0:
		# 	self.y = (1.0-self.decay)*self.y + self.stepSize*(i - 0.5)
		# 	self.drawStrip(self.canvas.p, self.y+0.5)
		# 	i = random.random()
		# 	drawsCount -= 1
		self.root.after(self.callbackDelay, self.mainLoop)

	def startDrawing(self):
		print "startDrawing() executed"
		if not self.drawingIsRunning:
			self.drawingIsRunning = True

	def resetDrawing(self):
		print "resetDrawing() executed"
		self.stopDrawing()
		self.clearGraph(self.canvas.p, self.bg)

	def stopDrawing(self):
		print "stopDrawing() executed"
		self.drawingIsRunning = False

	def clearGraph(self, p, color):
		self.x = 0
		self.lastY = 0.0
		self.y = 0.0
		p.tk.call(p, 'put', color, '-to', 0, 0, p["width"], p["height"])

	def scrollGraph(self, p):
		self.x = (self.x + 1) % self.w
		p.tk.call(p, 'put', self.bg, '-to', self.x, 0, self.x+1, self.h)
		p.tk.call(p, 'put', self.bg, '-to', self.x+self.w, 0, self.x+self.w+1, self.h)
		self.canvas.coords(self.image, -1-self.x, self.top)

	def drawStrip(self, p, y):
		if not self.lastY:
			self.lastY=y
		y0 = int( (self.h-1) * (1.0-self.lastY) )
		y1 = int( (self.h-1) * (1.0-y) )
		ymax = self.root.winfo_height()
		if y0 == y1:
			y1 += 1 
		y0, y1 = min(ymax, max(y0, 0)), min(ymax, max(y1, 0))
		ya, yb = min((y0,y1)), max((y0,y1))
		for y_interp in range(ya, yb):
			p.put(self.lineColor, (self.x, y_interp))
			p.put(self.lineColor, (self.x+self.w, y_interp))
		self.lastY = y
		pass

	def handleMsgs(self):
		if self.msgLock.acquire(False):
			while not self.messages.empty():
				msg = self.messages.get()
				if "command" in msg:
					command = msg["command"]
					if command == "set_bg":
						self.bg = msg["value"]
					elif command == "set_line_color":
						self.lineColor = msg["value"]
					elif command == "set_callback_delay":
						self.callbackDelay = msg["value"]
					elif command == "set_step_size":
						self.stepSize = msg["value"]
					elif command == "set_decay":
						self.decay = msg["value"]
					elif command == "set_extra_line_prob":
						self.density = msg["value"]
					elif command == "stop_drawing":
						self.stopDrawing()
					elif command == "reset_drawing":
						self.resetDrawing()
					elif command == "start_drawing":
						self.startDrawing()
					elif command == "quit":
						self.quit()
					elif command == "lie":
						self.lie()
				print "handled message:", msg
			self.msgLock.release()

	def lie(self):
		self.stepSize = self.MAX_STEP_SIZE
		self.decay = self.MAX_DECAY

	def adjustDrawParameters(self, floor=False):
		self.decay *= self.ddecay 
		self.stepSize *= self.dstep_size
		if floor:
			self.decay = max(self.MIN_DECAY, self.decay)
			self.stepSize = max(self.MIN_STEP_SIZE, self.stepSize)

	def quit(self):
		self.messageManager.close()
		self.hand.close()
		self.root.destroy()

def main():
    root = tk.Tk()
    root.title("Lie Graph")
    app = LieGraph(root)
    root.mainloop()

main()
