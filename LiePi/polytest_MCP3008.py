import pygame
import time
import random
import RPi.GPIO as GPIO
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from moteinopy import MoteinoNetwork
Event = pygame.fastevent.Event

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# define display surface
W, H = 720, 600

# initialise display
CLOCK = pygame.time.Clock()
pygame.init()
DS = pygame.display.set_mode((W, H),pygame.FULLSCREEN)
FPS = 100.00
MSPF = 2.00 / FPS

# Create event types
pygame.fastevent.init()

StartEventType = pygame.USEREVENT + 1
StopEventType = pygame.USEREVENT + 2

# StopEvent =  Event(StopEventType)

#Define Moteino stuff
moteino = MoteinoNetwork("/dev/ttyUSB0", base_id=53, init_base=False)
Pope = moteino.add_node(1, "int Command;", "DaPope")
Pope.add_translation("Command",
    ("Status", 99),
    ("Reset", 98),
    ("Start", 50))

def pope_receive(d):
    if d['Command'] == "Start":
        start_event = Event(StartEventType)
        pygame.fastevent.post(start_event)
    elif d['Command'] == "Reset":
        stop_event = Event(StopEventType)
        pygame.fastevent.post(stop_event)
    elif d['Command'] == "Status":
        Pope.send("Status")

Pope.bind(receive=pope_receive)


# Software SPI configuration (MCP3008):
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


# define some colors
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
LINECOLOR = BLACK

# define variables
shiftY = 100
freqset = 2
adcRead = 0
adcPrev = 1
draw = 1        # kveikt eda slokkt a linu a skja
counter = 1     # teljari fyrir linugerd
amplitude = 10
line_size = 5   # Thykkt linu
dot_size = 8    # ekki notad
dot_x = W - dot_size - shiftY    # ekki notad
del_y = 200
center_x = H / 2 + 20    #screen centerline
exit = False
startTime = time.time()
Timer = time.time()
keys=pygame.key.get_pressed()
pygame.mouse.set_visible(False) # hide mouse cursor
my = center_x           #draw line on Y-axis center
myPrev = my + 1
inc = 2
Amplitude = 0
divider = 15
flatline = 0


# main loop----------------------------------------------------------------------------------------------#
while True:
    if (GPIO.input(26) == False):
            exit = True
    for event in pygame.fastevent.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            exit = True         #ESC key exits program
        elif event.type == StopEventType:
            LINECOLOR = BLACK
        elif event.type == StartEventType:
            LINECOLOR = WHITE
    if exit: break
    #----------------------------------------------------------------------------------------------------#
    #if ( pygame.key.get_pressed()[pygame.K_SPACE] != 0 ):
        #LINECOLOR = WHITE
           # Wait for user input to start graph
    #----------------------------------------------------------------------------------------------------#

    adcRead = mcp.read_adc(0) / 4
    counter += 1
    amplitude = adcRead
    #----------BUTTONS---------------------------#
    #if (GPIO.input(16) == False):			#BUTTON 3
	# Unused function
    if (GPIO.input(20) == False):			#BUTTON 2
        amplitude = random.randrange(200, 255, 10)
    if (GPIO.input(21) == False):			#BUTTON 1
        amplitude = random.randrange(1, 15, 2)

    #--------------------------------------------#
    if amplitude <= 15:
        amplitude = random.randrange(1, 15, 2)
    freq = (256.00 - amplitude) / divider
    if freq <= 1: freq = 1
    if freq >= 4 and (adcRead >= 50): freq = 4
    if freq >= 4 and (adcRead <= 50): freq = 10
    if amplitude <= 15: freq = 30
    #----------------MAKE WAVEFORM-----------------------------------#
    flatline = 0

    if (GPIO.input(12) == True):                           # Handprint not present
        amplitude = 0
        flatline = 1

    if counter >= freq:
        #print freq
        #if amplitude >= 1:
        Amplitude = amplitude
        if flatline == 0: Amplitude = amplitude + random.randrange(5, 21, 2)
        counter = 1     #RESET COUNTER
        neg_amplitude = center_x - Amplitude    #define negative amplitude
        amp = center_x + Amplitude              #define positive amplitude

        if my <= myPrev  and my >=  neg_amplitude:
            myPrev = my
            my -=inc
        if my <= neg_amplitude:
            myPrev = my
            my = my + inc
        if my >= myPrev and my <= amp:
            myPrev = my
            my += inc
        if my >= amp:
            myPrev = my
            my = my - inc
        if my == center_x:
            amplitude = adcRead + random.randrange(10, 16, 2)

  #----------------DRAW WAVEFORM----------------------------------#
    if draw == 1:
        pygame.draw.line(DS, LINECOLOR, (dot_x, del_y), (dot_x, my), line_size)
        #pygame.draw.circle(DS, WHITE, (dot_x, my), dot_size, 0)
        del_y = my
    testTime = time.time()
    if testTime - startTime >= MSPF:
        startTime += MSPF
        DS.blit(DS, (0, 0), (1, 0, W - 1, H))
        pygame.display.update()


print("Quitting pygame and shutting down moteinonetwork")
pygame.quit()
moteino.shut_down()
