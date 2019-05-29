import threading
import time

def fun():
	while True:
		f = open("/home/campz/itworks.txt", "w+")
		f.write("See title")
		f.close()

t = threading.Thread(target=fun)
t.start()

time.sleep(1000)



