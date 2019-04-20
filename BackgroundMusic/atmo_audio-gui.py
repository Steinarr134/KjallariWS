# coding=utf-8
#from SocketCommunication import Server
import pygame
import time
from Tkinter import *
import tkMessageBox
#from Tkinter import messagebox

pygame.init()
#size = (500, 500)
sngtime = 0
sngtime2 = 0
sngtime3 = 0
sngtime4 = 0
MusicOn = 0
sngLength = 0


#---------- LOAD AUDIOFILES -----------------------------#
pygame.mixer.music.load("audio/bgndNoise.ogg")
snd1 = pygame.mixer.Sound('audio/warMusic1.ogg')
snd2 = pygame.mixer.Sound('audio/warMusic2.ogg')
snd3 = pygame.mixer.Sound('audio/warMusic3.ogg')
snd4 = pygame.mixer.Sound('audio/warMusic4.ogg')
snd5 = pygame.mixer.Sound('audio/shooter2.ogg')
snd6 = pygame.mixer.Sound('audio/stealth.ogg')
snd7 = pygame.mixer.Sound('audio/bomb.ogg')
snd8 = pygame.mixer.Sound('audio/winn.ogg')
snd9 = pygame.mixer.Sound('audio/loser.ogg')
buzzer = pygame.mixer.Sound('audio/buzzer4s.ogg')
sndWSwin = pygame.mixer.Sound('audio/voWin.ogg')
sndWSLose = pygame.mixer.Sound('audio/voLose.ogg')
sndWStimeout = pygame.mixer.Sound('audio/voTimeOut.ogg')

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
pygame.mixer.music.set_volume(0.3)
snd1.set_volume(0.1)  # Music #1
snd2.set_volume(0.1)  # Music #2
snd3.set_volume(0.1)  # Music #3
snd4.set_volume(0.1)  # Music #4
snd5.set_volume(0.3)  # Shooting Range Music
snd6.set_volume(0.6)  # Stealth Music
snd7.set_volume(0.9)  # BOMB Music
snd8.set_volume(0.6)  # WIN Music
snd9.set_volume(0.6)  # Lose Music
buzzer.set_volume(0.6)  # Timeout buzzer
sndWSwin.set_volume(1.0)  # WIN voice-over
sndWSLose.set_volume(1.0)  # LOSE voice-over
sndWStimeout.set_volume(1.0)  # Time ran out voice-over
#----------- SET CHANNEL LEVELS --------------#
sndCh1.set_volume(0.3)  # value 0.0 - 1.0
sndCh2.set_volume(0.8)  # value 0.0 - 1.0
sndCh3.set_volume(1.0)  # value 0.0 - 1.0
sndCh4.set_volume(1.0)  # value 0.0 - 1.0
sndCh5.set_volume(1.0)  # value 0.0 - 1.0
sndCh6.set_volume(1.0)  # value 0.0 - 1.0
sndCh7.set_volume(1.0)  # value 0.0 - 1.0
sndCh8.set_volume(1.0)  # value 0.0 - 1.0

frmbgd = "dim gray"   #Background colour
#---------------------------------------------------------------------------------
root = Tk()
root.title('CAMP-Z AUDIO')
root.geometry("500x550")
#root.overrideredirect(1) #Remove border
root.configure(bg=frmbgd)
root.resizable(width=False, height=False)

topFrame = Frame(root, bg=frmbgd, width=500, height=50, pady=3)
topFrame.pack(side=TOP)
bottomFrame = Frame(root, bg=frmbgd, width=500, height=50, pady=3)
bottomFrame.pack(side=BOTTOM)

leftFrame = Frame(root)
leftFrame.pack(side=LEFT)
rightFrame = Frame(root)
rightFrame.pack(side=RIGHT)

text1 = StringVar()
text2 = StringVar()
text3 = StringVar()
status = ""
status2 = ""
text1.set("All is quiet")
text2.set("Music not playing")
#---------------------------------------------------------------------#

def StartAudio():
    text1.set("Footsteps...")
    Status3Label.configure(bg=frmbgd)
    sndCh2.set_volume(0.8)
    pygame.mixer.music.play(-1) #LOOP PLAYBACK


def StartMusic():
    global audioBusy
    global MusicOn
    global sngtime
    text2.set("Playing Song #1")
    print ("song 1")
    MusicOn = 1
    audioBusy = 0
    Status3Label.configure(bg=frmbgd)
    sndCh2.set_volume(0.6)
    sndCh2.play(snd1)
    sngtime = time.time()


def MusicUnmute():
    global MusicOn
    global audioBusy
    text3.set("")
    audioBusy = 0
    if pygame.mixer.music.get_busy():
        text1.set("Footsteps...")
    Status3Label.configure(bg=frmbgd)
    sndCh3.stop()
    sndCh8.stop()

    if MusicOn == 1:
        text2.set("Playing Song #1")
    elif MusicOn == 2:
        text2.set("Playing Song #2")
    elif MusicOn == 3:
        text2.set("Playing Song #3")
    elif MusicOn == 4:
        text2.set("Playing Song #4")
    else:
        text2.set("Music not playing")
    #-------- FADE-IN -----------------
    pygame.mixer.music.play(-1)                                                                # Athuga ad nota while luppu
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


def StartLie():
    Status3Label.configure(bg="red")
    text3.set("ALL MUTED")
    if pygame.mixer.music.get_busy():
        text1.set("Shhhh....")
    #-------- FADE-OUT --------------
    sndCh2.set_volume(0.5)
    time.sleep(0.2)
    pygame.mixer.music.set_volume(0.0)
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


def StartShooting():
    global audioBusy
    audioBusy = 1
    text1.set("")
    text2.set("SHOOT 'EM UP!!")
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


def StartStealth():
    global audioBusy
    audioBusy = 1
    text1.set("")
    text2.set("SNEAKY...")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(snd6)


def StartBomb():
    global audioBusy
    audioBusy = 1
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(snd7)
    text1.set("")
    text2.set("IT'S A BOMB!!!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)


def StartWin():
    global audioBusy
    audioBusy = 1
    text1.set("")
    text2.set("VICTORIOUS!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(snd8)
    sndCh3.play(sndWSwin)


def StartLose():
    global audioBusy
    audioBusy = 1
    text1.set("")
    text2.set("YOU LOSE!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(snd9)
    sndCh3.play(sndWSLose)


def StartTimeout():
    global audioBusy
    audioBusy = 1
    text1.set("")
    text2.set("OUT OF TIME!")
    text3.set("")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.music.stop()
    sndCh2.stop()
    sndCh8.play(buzzer)
    sndCh3.play(sndWStimeout)


def KillAudio():
    global audioBusy
    audioBusy = 0
    text2.set("Music not playing")
    Status3Label.configure(bg=frmbgd)
    pygame.mixer.fadeout(1000)


StatusLabel = Label(bottomFrame, font=("Comic Sans MS", 14), textvariable=text1, fg="black", bg=frmbgd)
Status2Label = Label(bottomFrame, font=("Comic Sans MS", 14), textvariable=text2, fg="black", bg=frmbgd)
Status3Label = Label(bottomFrame, font=("Arial", 16, "bold"), textvariable=text3, fg="black")
StartBtn = Button(topFrame, font=("Comic Sans MS", 14), text="BACKGROUND NOISE", fg="gray", bg="forestgreen", command=StartAudio)
MusicBtn = Button(leftFrame, font=("Comic Sans MS", 14), width=24, text="START/RESTART MUSIC", fg="gray", bg="forestgreen", command=StartMusic)
LieBtn = Button(leftFrame, font=("Comic Sans MS", 14), width=24, text="LIE DETECTOR START", fg="gray", bg="forestgreen", command=StartLie)
MusicUnmuteBtn = Button(leftFrame, font=("Comic Sans MS", 14), width=24, text="LIE DETECTOR COMPLETE", fg="gray", bg="forestgreen", command=MusicUnmute)
ShootBtn = Button(leftFrame, font=("Comic Sans MS", 14), width=24, text="SHOOTING RANGE", fg="gray", bg="forestgreen", command=StartShooting)
StopShootBtn = Button(leftFrame, font=("Comic Sans MS", 14), width=24, text="SHOOTING RANGE DONE", fg="gray", bg="forestgreen", command=MusicUnmute)
StealthBtn = Button(leftFrame, font=("Comic Sans MS", 14), width=24, text="STEALTH", fg="gray", bg="forestgreen", command=StartStealth)
BombBtn = Button(leftFrame, font=("Comic Sans MS", 14), width=24, text="BOMB!!!", fg="gray", bg="forestgreen", command=StartBomb)
WinBtn = Button(rightFrame, font=("Comic Sans MS", 14), width=24, text="VICTORY", fg="gray", bg="forestgreen", command=StartWin)
LoseBtn = Button(rightFrame, font=("Comic Sans MS", 14), width=24, text="YOU LOSE", fg="gray", bg="forestgreen", command=StartLose)
TimeBtn = Button(rightFrame, font=("Comic Sans MS", 14), width=24, text="OUT OF TIME", fg="gray", bg="forestgreen", command=StartTimeout)
killBtn =  Button(topFrame, font=("Comic Sans MS", 14), text="KILL AUDIO", fg="gray", bg="red", command=KillAudio)
mussik = Label(root, font=('times', 20, 'bold'), bg='green')

Status3Label.configure(bg=frmbgd)

Status3Label.pack(side=BOTTOM)
Status2Label.pack(side=BOTTOM)
StatusLabel.pack(side=BOTTOM,)
StartBtn.pack(side=TOP, anchor=W, fill=X, expand=YES)
killBtn.pack(side=LEFT, fill=X, expand=YES)
MusicBtn.pack(side=TOP)
LieBtn.pack(side=TOP)
MusicUnmuteBtn.pack(side=TOP)
ShootBtn.pack(side=TOP)
StopShootBtn.pack(side=TOP)
StealthBtn.pack(side=TOP)
BombBtn.pack(side=TOP)
WinBtn.pack(side=BOTTOM)
LoseBtn.pack(side=BOTTOM)
TimeBtn.pack(side=BOTTOM)


def playMusic():
    global audioBusy
    global MusicOn
    global sngtime
    global sngtime2
    global sngtime3
    global sngtime4
    if MusicOn == 1 and time.time() - sngtime > 1128:        #1128:
        if audioBusy == 0:
            text2.set("Playing Song #2")
            print ("song 2")
        sndCh2.play(snd2)
        sngtime2 = time.time()
        MusicOn = 2

    if MusicOn == 2 and time.time() - sngtime2 > 1046:       #1046:
        if audioBusy == 0:
            text2.set("Playing Song #3")
            print ("song 3")
        sndCh2.play(snd3)
        sngtime3 = time.time()
        MusicOn = 3

    if MusicOn == 3 and time.time() - sngtime3 > 1102:       #1102
            MusicOn = 4
            if audioBusy == 0:
                text2.set("Playing Song #4")
                print ("song 4")
            sndCh2.play(snd4)
            sngtime4 = time.time()

    if MusicOn == 4 and time.time() - sngtime4 > 1226:      #1226
            MusicOn = 1
            if audioBusy == 0:
                text2.set("Playing Song #1.... again!")
                print ("song 1 again")
            sndCh2.play(snd1)
            sngtime = time.time()
    # LOOP FUNCTION
    mussik.after(200, playMusic)


playMusic()

def on_closing():
    if tkMessageBox.askokcancel("Stop ALL audio...", "Quitting program will stop all background audio, /n Do you REALLY want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
#---------------------------------------------------------------------------------
