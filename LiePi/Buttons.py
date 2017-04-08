# Import gpio library
import RPi.GPIO as GPIO
import time

class Buttons:
	BUTTON_PINS = [12, 6, 5, 7, 8, 11, 9]
	LIGHT_PINS  = [25, 10, 24, 23, 22, 27, 18]
	SLEEP_DURATION = 0.04
	last_read = [False for i in range(len(BUTTON_PINS))]
	button_states = [False for i in range(len(BUTTON_PINS))]
	key = [4,3,2,1]	
	sequence = []
	
	is_running = False

	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		for pin in self.BUTTON_PINS:
			GPIO.setup(pin, GPIO.IN)
		for pin in self.LIGHT_PINS:
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, GPIO.HIGH) # Slokkt ljos
		self.init()

	def init(self):
		self.is_running = True
		self.read_strategy = self.scene_selection_read
		self.readButtons()

	def set_strategy_default(self):
		self.read_strategy = self.default_read

	def activate_combination_lock(self):
		self.read_strategy = self.combination_lock_read

	def activate_scene_selection(self):
		self.read_strategy = self.scene_selection_read

	def readButtons(self):
		while self.is_running:
			for i,pin in enumerate(self.BUTTON_PINS):
				read = not GPIO.input(pin)
				self.read_strategy(i, read)
				# self.default_read(i, read)
				self.last_read[i] = read
			time.sleep(self.SLEEP_DURATION)

	def default_read(self, i, read):
		current = self.button_states[i]
		prev = self.last_read[i]
		next = (current and read) or (current and prev) or (read and prev)
		if next ^ current:
			if next:
				GPIO.output(self.LIGHT_PINS[i], GPIO.LOW)
			else:
				GPIO.output(self.LIGHT_PINS[i], GPIO.HIGH)
		self.button_states[i] = next


	def combination_lock_read(self, i, read):
		current = self.button_states[i]
		prev = self.last_read[i]
		next = (current and read) or (current and prev) or (read and prev)
		if next and not current:
			self.push(i)

	def scene_selection_read(self, i, read):
		current = self.button_states[i]
		prev = self.last_read[i]
		next = (current and read) or (current and prev) or (read and prev)
		if next and not current and sum(self.button_states) == 0 and i<=4:
			self.button_states[i] = True
			GPIO.output(self.LIGHT_PINS[i], GPIO.LOW)
		elif next and not current and i == 6:
			for pin in self.LIGHT_PINS:
				GPIO.output(pin, GPIO.HIGH)
			self.button_states = [False for _ in self.button_states]

	def send_scene(self):
		pass

	def badseq(self):
		for pin in self.LIGHT_PINS:
			GPIO.output(pin, GPIO.HIGH)
		GPIO.output(self.LIGHT_PINS[-1], GPIO.LOW)
		time.sleep(1)
		GPIO.output(self.LIGHT_PINS[-1], GPIO.HIGH)
		self.button_states = [False for _ in self.button_states]

	def goodseq(self):
		for pin in self.LIGHT_PINS:
			GPIO.output(pin, GPIO.HIGH)
		GPIO.output(self.LIGHT_PINS[-2], GPIO.LOW)
		time.sleep(1)
		GPIO.output(self.LIGHT_PINS[-2], GPIO.HIGH)
		self.button_states = [False for _ in self.button_states]

	def push(self, digit):
		if digit not in self.sequence and len(self.sequence)<len(self.key) and digit <= 4:
			self.sequence.append(digit)
			GPIO.output(self.LIGHT_PINS[digit], GPIO.LOW)
			time.sleep(0.1)
		if len(self.sequence) == len(self.key):
			if self.sequence == self.key:
				self.goodseq()
			else:
				self.badseq()
		self.sequence = []




# if button state changes and persists for some time
# use messageManager from LiePie to send message to the pope

# close