# coding=utf-8
from SocketCom import Server
import pygame
import time
from Tkinter import *
import tkMessageBox

#http://www.science.smith.edu/dftwiki/images/3/3d/TkInterColorCharts.png

pygame.init()
sngtime = 0
sngtime2 = 0
sngtime3 = 0
sngtime4 = 0
MusicOn = 0
sngLength = 0
audioBusy = False


# ---------- LOAD AUDIOFILES ----------------------------- #
# pygame.mixer.music.load("audio/bgndNoise.ogg")
snd1 = pygame.mixer.Sound('audio/warMusic1.ogg')
snd2 = pygame.mixer.Sound('audio/warMusic2.ogg')
snd3 = pygame.mixer.Sound('audio/warMusic3.ogg')
snd4 = pygame.mixer.Sound('audio/warMusic4.ogg')
snd5 = pygame.mixer.Sound('audio/shooter2.ogg')
snd6 = pygame.mixer.Sound('audio/stealth.ogg')
snd7 = pygame.mixer.Sound('audio/bomb.ogg')
snd8 = pygame.mixer.Sound('audio/winn.ogg')
snd9 = pygame.mixer.Sound('audio/loser.ogg')
snd10 = pygame.mixer.Sound('audio/lieDefault.ogg')
snd11 = pygame.mixer.Sound('audio/factory.ogg')
snd12 = pygame.mixer.Sound('audio/passport.ogg')
snd13 = pygame.mixer.Sound('audio/map.ogg')
snd14 = pygame.mixer.Sound('audio/elevator.ogg')
snd15 = pygame.mixer.Sound('audio/winTemp.ogg')
buzzer = pygame.mixer.Sound('audio/buzzer4s.ogg')
buzzer2 = pygame.mixer.Sound('audio/buzzer1s.ogg')
sndWSwin = pygame.mixer.Sound('audio/voWin.ogg')
sndWSLose = pygame.mixer.Sound('audio/voLose.ogg')
sndWStimeout = pygame.mixer.Sound('audio/voTimeOut.ogg')
snd16 = pygame.mixer.Sound('audio/10min.ogg')
snd17 = pygame.mixer.Sound('audio/5min.ogg')
snd18 = pygame.mixer.Sound('audio/3min.ogg')
snd19 = pygame.mixer.Sound('audio/1min.ogg')
snd20 = pygame.mixer.Sound('audio/bombStart.ogg')


# ---------------------SET UP AUDIO CHANNELS ---------------------#
sndCh1 = pygame.mixer.Channel(0)
sndCh2 = pygame.mixer.Channel(1)
sndCh3 = pygame.mixer.Channel(2)
sndCh4 = pygame.mixer.Channel(3)
sndCh5 = pygame.mixer.Channel(4)
sndCh6 = pygame.mixer.Channel(5)
sndCh7 = pygame.mixer.Channel(6)
sndCh8 = pygame.mixer.Channel(7)

# ------ SET FILE LEVELS--------------#
# pygame.mixer.music.set_volume(0.3)
snd1.set_volume(0.1)  # Music #1
snd2.set_volume(0.1)  # Music #2
snd3.set_volume(0.1)  # Music #3
snd4.set_volume(0.1)  # Music #4
snd5.set_volume(0.8)  # Shooting Range Music
snd6.set_volume(0.6)  # Stealth Music
snd7.set_volume(0.9)  # BOMB Music
snd8.set_volume(0.6)  # WIN Music
snd9.set_volume(0.6)  # Lose Music
snd10.set_volume(0.3) # Default lie detector music
snd11.set_volume(0.15) # Mission 1 factory atmo
snd12.set_volume(0.25) # mission 2 passport atmo
snd13.set_volume(0.25) # mission 3 map atmo
snd14.set_volume(0.9) # elevator atmo
# snd15.set_volume(0.8) # Win sound Mission
buzzer.set_volume(0.6)  # Timeout buzzer
buzzer2.set_volume(0.6)  # Short buzzer
sndWSwin.set_volume(1.0)  # WIN voice-over
sndWSLose.set_volume(1.0)  # LOSE voice-over
sndWStimeout.set_volume(1.0)  # Time ran out voice-over
# ----------- SET CHANNEL LEVELS -------------- #
sndCh1.set_volume(0.3)  # value 0.0 - 1.0
sndCh2.set_volume(0.8)  # value 0.0 - 1.0
sndCh3.set_volume(1.0)  # value 0.0 - 1.0
sndCh4.set_volume(0.4)  # value 0.0 - 1.0
sndCh5.set_volume(0.4)  # value 0.0 - 1.0
sndCh6.set_volume(1.0)  # value 0.0 - 1.0
sndCh7.set_volume(1.0)  # value 0.0 - 1.0
sndCh8.set_volume(1.0)  # value 0.0 - 1.0

frmbgd = "light slate gray"   # Background colour
btnfg = "black"       # Button text color
btnbg = "white smoke"      # Button background color
btnactbg = "light goldenrod"     # Button color when mouse over
noAudioBtnactbg = "tomato"

# --------------------------------------------------------------------------------- #
root = Tk()
root.title('CAMP-Z AUDIO')                  # Window title
root.geometry("500x700")                    # Window size
root.configure(bg=frmbgd)                   # Window fill color
root.resizable(width=False, height=False)   # Window not resizable

# ------------ SET FRAME SIZES / PLACE FRAMES ---------#
topFrame = Frame(root, bg=frmbgd, width=500, height=50, pady=3)
topFrame.pack(side=TOP)
bottomFrame = Frame(root, bg=frmbgd, width=500, height=50, pady=3)
bottomFrame.pack(side=BOTTOM)
leftFrame = Frame(root)
leftFrame.pack(side=LEFT)
rightFrame = Frame(root)
rightFrame.pack(side=RIGHT)
# -----------------------------------------------------#

text1 = StringVar()
text2 = StringVar()
text3 = StringVar()
status = ""
status2 = ""
text1.set("All is quiet")           # INFO TEXT1 DEFAULT
text2.set("Music not playing")      # INFO TEXT2 DEFAULT
# --------------------------------------------------------------------- #


def audio_busy(truefalse):
    global audioBusy
    audioBusy = truefalse
    if not audioBusy:
        playMusic()


def StartingAtmo():        # ELEVATOR NOISE, BEFORE ESCAPING ELEVATOR
    # text1.set("")
    text2.set("Playing:  Starting atmo")
    text3.set("")
    pygame.mixer.music.load('audio/elevator.ogg')
    pygame.mixer.music.set_volume(1.3)
    pygame.mixer.music.play(-1)  # LOOP PLAYBACK

def StartAudio():           # BAKGRUNNSHLJÓÐ, footsteps etc
    pygame.mixer.music.fadeout(500)
    time.sleep(5)
    text1.set("Footsteps playing in background")
    Status3Label.configure(bg=frmbgd)
    sndCh2.set_volume(0.8)
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.load("audio/bgndNoise.ogg")
    pygame.mixer.music.play(-1)  # LOOP PLAYBACK


def StartMusic():           # RÆSA SÍSPILANDI BAKGRUNNS-TÓNLIST
    print("Started music without asked!")

    global MusicOn
    global sngtime
    text2.set("Playing:  Song #1")
    print ("song 1")
    print time.strftime('%H:%M:%S')
    MusicOn = 1
    Status3Label.configure(bg=frmbgd)
    sndCh2.set_volume(0.6)
    sndCh2.play(snd1)
    sngtime = time.time()
    audio_busy(False)


def MusicUnmute():          # EFTIR LIE DETECTOR / SHOOTING RANGE
    StartAudio()
    global MusicOn
    text3.set("")
    audio_busy(False)
    if pygame.mixer.music.get_busy():
        text1.set("Footsteps...")
    Status3Label.configure(bg=frmbgd)
    sndCh3.stop()
    sndCh8.stop()
    sndCh4.stop()
    StartMusic()

    if MusicOn == 1:
        text2.set("Playing:  Song #1")
    elif MusicOn == 2:
        text2.set("Playing:  Song #2")
    elif MusicOn == 3:
        text2.set("Playing:  Song #3")
    elif MusicOn == 4:
        text2.set("Playing:  Song #4")
    else:
        text2.set("Music not playing")
    # -------- FADE-IN ----------------- #
    pygame.mixer.music.play(-1)
    sndCh2.set_volume(0.1)
    pygame.mixer.music.set_volume(0.1)
    time.sleep(0.2)
    sndCh2.set_volume(0.2)
    pygame.mixer.music.set_volume(0.2)
    time.sleep(0.2)
    sndCh2.set_volume(0.3)
    pygame.mixer.music.set_volume(0.3)
    time.sleep(0.2)
    sndCh2.set_volume(0.4)
    time.sleep(0.2)
    sndCh2.set_volume(0.5)
    time.sleep(0.2)
    sndCh2.set_volume(0.6)
    time.sleep(0.2)


def StartLie():             # LIE DETECTOR START

    text1.set("")
    text2.set("Playing:  Lie Detector Default")
    text3.set("")

    if pygame.mixer.music.get_busy():
        text1.set("Shhhh....")

    sndCh4.stop()
    StartMusic()

    # -------- FADE-OUT -------------- #
    sndCh2.set_volume(0.5)
    time.sleep(0.2)
    sndCh2.set_volume(0.4)
    time.sleep(0.2)
    sndCh2.set_volume(0.3)


#MISSION 1: FACTORY
def StartMisFact():
    text1.set("")
    text2.set("Playing:  Factory atmo")
    text3.set("")
    audio_busy(True)
    pygame.mixer.music.set_volume(0.0)
    sndCh4.play(snd11)
    sndCh2.stop()


#MISSION 2: PASSPORT
def StartMisPass():
    text1.set("")
    text2.set("Playing:  Passport atmo")
    text3.set("")
    audio_busy(True)
    pygame.mixer.music.set_volume(0.0)
    sndCh4.play(snd12)
    sndCh2.stop()

#MISSION 3: MAP
def StartMisMap():
    text1.set("")
    text2.set("Playing:  Map atmo")
    text3.set("")
    audio_busy(True)
    pygame.mixer.music.set_volume(0.0)
    sndCh2.stop()
    sndCh4.play(snd13)

def WrongAnswer():
    sndCh5.play(buzzer2)

def TenMin():
    sndCh5.play(snd16)

def FiveMin():
    sndCh5.play(snd17)

def ThreeMin():
    sndCh5.play(snd18)

def OneMin():
    sndCh5.play(snd19)

def BombStart():
    sndCh5.play(snd20)

def StartShooting():            # SHOOTING RANGE
    audio_busy(True)
    text1.set("")
    text2.set("Playing: SHOOT 'EM UP!!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.set_volume(0.0)
    sndCh2.set_volume(0.5)
    time.sleep(0.2)
    sndCh2.set_volume(0.4)
    time.sleep(0.2)
    sndCh2.set_volume(0.3)
    time.sleep(0.2)
    sndCh2.set_volume(0.2)
    time.sleep(0.2)
    sndCh2.set_volume(0.1)
    time.sleep(0.2)
    sndCh2.set_volume(0.0)
    time.sleep(0.2)
    sndCh8.play(snd5)


def StartStealth():             # STEALTH MODE
    audio_busy(True)
    text1.set("")
    text2.set("Playing: SNEAKY...")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(snd6)


def StartBomb():                # KABOOM
    audio_busy(True)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(snd7)
    text1.set("")
    text2.set("Playing: IT'S A BOMB!!!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)


def StartWin():                 # VICTORY!!!
    audio_busy(True)
    text1.set("")
    text2.set("Playing: VICTORIOUS!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(snd8)
    sndCh3.play(sndWSwin)


def StartLose():                # YOU LOSE!
    audio_busy(True)
    text1.set("")
    text2.set("Playing: YOU LOSE!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(snd9)
    sndCh3.play(sndWSLose)


def StartTimeout():             #TIME RAN OUT
    audio_busy(True)
    text1.set("")
    text2.set("Playing: OUT OF TIME!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(buzzer)
    sndCh3.play(sndWStimeout)


def KillAudio():                # KILL ALL AUDIO
    audio_busy(False)
    pygame.mixer.music.stop()
    text2.set("Music not playing")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.fadeout(1000)


pairing = {}

StatusLabel = Label(bottomFrame, font=("Arial", 14), textvariable=text1, fg="black", bg=frmbgd)
Status2Label = Label(bottomFrame, font=("Arial", 14), textvariable=text2, fg="black", bg=frmbgd)
Status3Label = Label(bottomFrame, font=("Arial", 16, "bold"), textvariable=text3, fg="black")


StartBtn = Button(topFrame, font=("Arial", 14), text="BACKGROUND NOISE", fg=btnfg,
                  bg=btnbg, activebackground=btnactbg, command=StartAudio)
pairing["StartAudio"] = StartAudio
pairing["BACKGROUND NOISE"] = StartAudio

MusicBtn = Button(leftFrame, font=("Arial", 14), width=24, text="START/RESTART MUSIC", fg=btnfg,
                  bg=btnbg, activebackground=btnactbg, command=StartMusic)
pairing["StartMusic"] = StartMusic
pairing["START/RESTART MUSIC"] = StartMusic

LieBtn = Button(leftFrame, font=("Arial", 14), width=24, text="LIE DETECTOR START", fg=btnfg,
                bg=btnbg, activebackground=btnactbg, command=StartLie)
pairing["StartLie"] = StartLie
pairing["LIE DETECTOR START"] = StartLie

#elevator button
StartingAtmoBtn = Button(topFrame, font=("Arial", 14), text="STARTING ATMO", fg=btnfg,
                  bg=btnbg, activebackground=btnactbg, command=StartingAtmo)
pairing["STARTING ATMO"] = StartingAtmo
pairing["STARTING ATMO"] = StartingAtmo

#MISSION 1: FACTORY
Mission1Btn = Button(leftFrame, font=("Arial", 14), width=24, text="MISSION 1 FACTORY START", fg=btnfg,
                bg=btnbg, activebackground=btnactbg, command=StartMisFact)
pairing["StartMisFact"] = StartMisFact
pairing["MISSION 1 FACTORY START"] = StartMisFact

#MISSION 2: PASSPORT
Mission2Btn = Button(leftFrame, font=("Arial", 14), width=24, text="MISSION 2 PASSPORT START", fg=btnfg,
                bg=btnbg, activebackground=btnactbg, command=StartMisPass)
pairing["StartMisPass"] = StartMisPass
pairing["MISSION 2 PASSPORT START"] = StartMisPass

#MISSION 3: MAP
Mission3Btn = Button(leftFrame, font=("Arial", 14), width=24, text="MISSION 3 MAP START", fg=btnfg,
                bg=btnbg, activebackground=btnactbg, command=StartMisMap)
pairing["StartMisMap"] = StartMisMap
pairing["MISSION 3 MAP START"] = StartMisMap


MusicUnmuteBtn = Button(leftFrame, font=("Arial", 14), width=24, text="LIE DETECTOR COMPLETE",
                        fg=btnfg, activebackground=btnactbg, bg=btnbg, command=MusicUnmute)
pairing["MusicUnmute"] = MusicUnmute
pairing["LIE DETECTOR COMPLETE"] = MusicUnmute

ShootBtn = Button(leftFrame, font=("Arial", 14), width=24, text="SHOOTING RANGE", fg=btnfg,
                  bg=btnbg, activebackground=btnactbg, command=StartShooting)
pairing["StartShooting"] = StartShooting
pairing["SHOOTING RANGE"] = StartShooting

StopShootBtn = Button(leftFrame, font=("Arial", 14), width=24, text="SHOOTING RANGE DONE",
                      fg=btnfg, activebackground=btnactbg, bg=btnbg, command=MusicUnmute)
pairing["MusicUnmute"] = MusicUnmute
pairing["SHOOTING RANGE DONE"] = MusicUnmute

StealthBtn = Button(leftFrame, font=("Arial", 14), width=24, text="STEALTH", fg=btnfg,
                    bg=btnbg, activebackground=btnactbg, command=StartStealth)
pairing["StartStealth"] = StartStealth
pairing["STEALTH"] = StartStealth

BombBtn = Button(leftFrame, font=("Arial", 14), width=24, text="BOMB!!!", fg=btnfg,
                 bg=btnbg, activebackground=btnactbg, command=StartBomb)
pairing["StartBomb"] = StartBomb
pairing["BOMB!!!"] = StartBomb
pairing["BOMB"] = StartBomb

WinBtn = Button(rightFrame, font=("Arial", 20, "bold"), width=24, text="VICTORY", fg=btnfg,
                bg="green", activebackground=btnactbg, command=StartWin)
pairing["StartWin"] = StartWin
pairing["VICTORY"] = StartWin

LoseBtn = Button(rightFrame, font=("Arial", 20, "bold"), width=24, text="EXPLODED", fg=btnfg,
                 bg="orange", activebackground=btnactbg, command=StartLose)
pairing["EXPLODED"] = StartLose
pairing["EXPLODED"] = StartLose

TimeBtn = Button(rightFrame, font=("Arial", 20, "bold"), width=24, text="OUT OF TIME", fg=btnfg,
                 bg="red", activebackground=btnactbg, command=StartTimeout)
pairing["StartTimeout"] = StartTimeout
pairing["OUT OF TIME"] = StartTimeout

WrongBtn = Button(rightFrame, font=("Arial", 20), width=24, text="Wrong Answer", fg=btnfg,
                 bg="red4", activebackground=btnactbg, command=WrongAnswer)
pairing["Wrong Answer"] = WrongAnswer
# pairing["WRONG ANSWER"] = WrongAnswer

TenMinBtn = Button(rightFrame, font=("Arial", 20), width=24, text="10 Min left", fg=btnfg,
                 bg="yellow", activebackground=btnactbg, command=TenMin)
pairing["10 Min left"] = TenMin
pairing["10min"] = TenMin

FiveMinBtn = Button(rightFrame, font=("Arial", 20), width=24, text="5 Min left", fg=btnfg,
                 bg="yellow", activebackground=btnactbg, command=FiveMin)
pairing["5 Min left"] = FiveMin
pairing["5min"] = FiveMin

ThreeMinBtn = Button(rightFrame, font=("Arial", 20), width=24, text="3 Min left", fg=btnfg,
                 bg="yellow", activebackground=btnactbg, command=ThreeMin)
pairing["3 Min left"] = ThreeMin
pairing["3min"] = ThreeMin

OneMinBtn = Button(rightFrame, font=("Arial", 20), width=24, text="1 Min left", fg=btnfg,
                 bg="yellow", activebackground=btnactbg, command=OneMin)
pairing["1 Min left"] = OneMin
pairing["1min"] = OneMin

BombStartBtn = Button(rightFrame, font=("Arial", 20), width=24, text="Bomb Start", fg=btnfg,
                 bg="medium slate blue", activebackground=btnactbg, command=BombStart)
pairing["Bomb Start"] = BombStart
pairing["bombStart"] = BombStart

killBtn = Button(topFrame, font=("Arial", 14, "bold"), text="KILL AUDIO", fg="black",
                 bg="red", activebackground=noAudioBtnactbg, command=KillAudio)
pairing["KillAudio"] = KillAudio
pairing["KILL AUDIO"] = KillAudio


mussik = Label(root, font=('times', 20, 'bold'), bg='green')

Status3Label.configure(bg=frmbgd)

Status3Label.pack(side=BOTTOM)
Status2Label.pack(side=BOTTOM)
StatusLabel.pack(side=BOTTOM,)
StartBtn.pack(side=TOP, anchor=W, fill=X, expand=YES)
killBtn.pack(side=LEFT, fill=X, expand=YES)
MusicBtn.pack(side=TOP)
StartingAtmoBtn.pack(side=TOP)
LieBtn.pack(side=TOP)
Mission1Btn.pack(side=TOP)
Mission2Btn.pack(side=TOP)
Mission3Btn.pack(side=TOP)
MusicUnmuteBtn.pack(side=TOP)
ShootBtn.pack(side=TOP)
StopShootBtn.pack(side=TOP)
StealthBtn.pack(side=TOP)
BombBtn.pack(side=TOP, padx=2, pady=2)
BombStartBtn.pack(side=TOP, padx=2, pady=2)
WinBtn.pack(side=BOTTOM)
LoseBtn.pack(side=BOTTOM)
TimeBtn.pack(side=BOTTOM)
OneMinBtn.pack(side=BOTTOM)
ThreeMinBtn.pack(side=BOTTOM)
FiveMinBtn.pack(side=BOTTOM)
TenMinBtn.pack(side=BOTTOM)
WrongBtn.pack(side=BOTTOM)
WinBtn.pack(side=BOTTOM)


def playMusic():                # SONG QUEUE
    global MusicOn
    global sngtime
    global sngtime2
    global sngtime3
    global sngtime4

    if MusicOn == 1 and time.time() - sngtime > 1128:        # 1128:
        if audioBusy == 0:
            text2.set("Playing Song #2")
            print ("song 2")
            print time.strftime('%H:%M:%S')
        sndCh2.play(snd2)
        sngtime2 = time.time()
        MusicOn = 2

    if MusicOn == 2 and time.time() - sngtime2 > 1046:       # 1046:
        if audioBusy == 0:
            text2.set("Playing Song #3")
            print ("song 3")
            print time.strftime('%H:%M:%S')
        sndCh2.play(snd3)
        sngtime3 = time.time()
        MusicOn = 3

    if MusicOn == 3 and time.time() - sngtime3 > 1102:       # 1102
            MusicOn = 4
            if audioBusy == 0:
                text2.set("Playing Song #4")
                print ("song 4")
                print time.strftime('%H:%M:%S')
            sndCh2.play(snd4)
            sngtime4 = time.time()

    if MusicOn == 4 and time.time() - sngtime4 > 1226:      # 1226
            MusicOn = 1
            if audioBusy == 0:
                text2.set("Playing Song #1.... again!")
                print ("song 1 again")
                print time.strftime('%H:%M:%S')
            sndCh2.play(snd1)
            sngtime = time.time()

    # LOOP FUNCTION
    # print("'loopfunction' ",audioBusy)
    if not audioBusy:
        mussik.after(1, playMusic)


def on_closing():               # QUIT WARNING WINDOW
    if tkMessageBox.askokcancel("!!WARNING - WARNING - WARNING!!",
                                "Quitting program will stop all background audio,\n Do you REALLY want to quit?"):
        root.destroy()


def handle(msg):
    if msg.upper() in pairing:
        pairing[msg.upper()]()
    elif msg in pairing:
        pairing[msg]()


if __name__ == '__main__':
    server = Server(handle, port=3022)
    playMusic()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
# ---------------------------------------------------------------------------------#
