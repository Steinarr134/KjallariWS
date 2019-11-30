import Tkinter as tk
from tkMessageBox import askquestion
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import Queue
from Config import *
from HelperStuff import HintLoaderClass

# Possibly Persistant values
class GlobalValues(object):
    def __init__(self):
        self.ClockHasStarted = False
        self.ClockStartTime = None
        self.StealthActive = True
        self.NotifyQHistory = []
        # self.LieDetectorScenesAvailable = [None, None, None]
        # self.LieDetectorCurrentSceneNumber = None
        # self.LieDetectorCurrentSceneCurrentFileNumber = None


globals = GlobalValues()


top = tk.Tk()
top.attributes("-fullscreen", True)
# top.withdraw()

"""
To Do in this skjal

- Fix variable names to comply with pep (uneccessary, I know)
- Create a frame around SplitFlap stuff and pack inside the frame
    ~ So that it has the same build as everything else
-


"""

FailButtonNames = [
    "Elevator Escape",
    "Start TapeRecorder",
    "Open Safe",
    "GreenDude Fail",
    "Start Lie Detector",
    "Lie Detector Fail",
    "Open WineBox",
    "Shooting Range Fail",
    "Morse Fail",
    "Stealth Fail",
    "Start TimeBomb"
]


# Init Window
def player_info(exit_button_callback, info={}):
    window = tk.Tk()
    window.resizable(width=False, height=False)
    window.geometry("{}x{}".format(300, 200))
    
    number_of_players_frame = tk.Frame(window)
    number_of_players_frame.pack(side=tk.TOP)
    number_of_players_label = tk.Label(number_of_players_frame, text="Number Of Players: ")
    number_of_players_label.pack(side=tk.LEFT)
    number_of_players_entry = tk.Entry(number_of_players_frame, bd=1, width=5)
    number_of_players_entry.pack(side=tk.RIGHT)
    number_of_players_entry.focus()
    
    age_range_frame = tk.Frame(window)
    age_range_frame.pack(side=tk.TOP)
    age_range_label1 = tk.Label(age_range_frame, text="Age Range (circa):  From")
    age_range_entry1 = tk.Entry(age_range_frame, bd=1, width=5)
    age_range_label2 = tk.Label(age_range_frame, text=" to ")
    age_range_entry2 = tk.Entry(age_range_frame, bd=1, width=5)
    age_range_label1.pack(side=tk.LEFT)
    age_range_entry1.pack(side=tk.LEFT)
    age_range_label2.pack(side=tk.LEFT)
    age_range_entry2.pack(side=tk.LEFT)
    
    NationalityOptions = ["Iceland", "Europe", "North America", "Other"]
    NationalityFrame = tk.Frame(window)
    NationalityFrame.pack(side=tk.TOP)
    NationalityLabel = tk.Label(NationalityFrame, text="Mostly from ")
    Nationality = tk.StringVar(window)
    Nationality.set(NationalityOptions[0])
    NationaliityOptionMenu = tk.OptionMenu(NationalityFrame, Nationality, *NationalityOptions)
    NationaliityOptionMenu.configure(takefocus=True)
    
    NationalityLabel.pack(side=tk.LEFT)
    NationaliityOptionMenu.pack(side=tk.LEFT)
    
    GenderOptions = ["Males", "Females", "Both/Other"]
    GenderFrame = tk.Frame(window)
    GenderFrame.pack(side=tk.TOP)
    GenderLabel = tk.Label(GenderFrame, text="Gender: ")
    Gender = tk.StringVar(window)
    Gender.set(GenderOptions[0])
    GenderOptionMenu = tk.OptionMenu(GenderFrame, Gender, *GenderOptions)
    GenderOptionMenu.configure(takefocus=True)
    GenderLabel.pack(side=tk.LEFT)
    GenderOptionMenu.pack(side=tk.LEFT)

    # closes this window and calls the exit_button_callback passing player info
    def exit_init_window(event=None):
        # top.deiconify()
        ret_player_info = {"NofPlayers": int(number_of_players_entry.get().strip()),
                           "more info": "some info"}
        window.destroy()
        exit_button_callback(ret_player_info)

    AboutPlayersSubmitButton = tk.Button(window, text="Submit", command=exit_init_window)
    AboutPlayersSubmitButton.pack(side=tk.BOTTOM)



# Menu
Menu = tk.Menu(top)
top.config(menu=Menu)

ActionMenu = tk.Menu(Menu, tearoff=False)
Menu.add_cascade(label='Actions', menu=ActionMenu)
Actions = ["Check All Device Status",
           "Reset Room",
           "New Group"]

DeviceMenu = tk.Menu(Menu, tearoff=False)
Menu.add_cascade(label="Devices", menu=DeviceMenu)
for device in Devices:
    submenu = tk.Menu(DeviceMenu, tearoff=False)
    DeviceMenu.add_cascade(label=device, menu=submenu)
    DeviceSubmenus.append(submenu)


# SplitFlap
SplitFlapEntry = tk.Text(top, bd=5, width=20, height=5, font="Verdana 16")
SplitFlapEntry.place(x=50, y=100)
SplitFlapEntryButton = tk.Button(top, text="Send hint")
SplitFlapEntryButton.place(x=325, y=150)
SplitFlapEntryClearButton = tk.Button(top, text="Clear")
SplitFlapEntryClearButton.place(x=325, y=200)
SplitFlapDisplayLabel = tk.Label(top,
                                 text="Now displaying: '           '",
                                 font="Verdana 12 bold")
SplitFlapDisplayLabel.place(x=50, y=250)


def clear_split_flap_entry(event=None):
    SplitFlapEntry.delete(0., tk.END)


SplitFlapEntryClearButton.bind("<Button-1>", clear_split_flap_entry)

def fix_split_flap_input(event=None):
    # print "'" + event.char + "'"
    if event.char:
        stuff = SplitFlapEntry.get(1.0, tk.END)
        # print stuff.split('\n')
        last_part = stuff.split('\n')[-2]
        # print "len: " + str(len(last_part))
        if len(last_part) > 10:
            SplitFlapEntry.insert(float(len(stuff)), '\n')

SplitFlapEntry.bind("<Key>", fix_split_flap_input)
SplitFlapEntry.bind("<BackSpace>", lambda event: None)


# Progress Plot
ProgressPlotFigure = Figure(figsize=(8, 4), dpi=50)
ProgressPlotBaseLine = cumsum([0,
                               2*60,  # Press play on TapeRecorder
                               8*60,  # LockPicking
                               5*60,  # GreenDude
                               7*60,  # Rod
                               10*60,  # LieDetector
                               3*60,  # WineCase
                               10*60,  # Shooting Range
                               2*60,   # Morse
                               10*60,  # Stealth
                               5*60])  # Bomb
ProgressPlotCanvas = FigureCanvasTkAgg(ProgressPlotFigure, master=top)
ProgressPlotCanvas.get_tk_widget().place(x=25, y=300)


def update_progress_plot(times):
    ProgressPlotFigure.clear()
    p = ProgressPlotFigure.add_subplot(111)
    p.plot(range(11), ProgressPlotBaseLine, color="r")
    print "plot times: {}".format(times)
    p.plot(range(len(times)), times)
    ProgressPlotCanvas.draw()



# Log Text
LogTextWidget = tk.Text(top, height=20, width=75, font="helvetica 10")
LogTextWidget.place(x=500, y=25)
LogTextWidget.insert('end', " System starting...")
LogTextWidget['state'] = 'disabled'
LogTextWidget.tag_configure("warning", foreground="#ff0000", font="helvetica 10 bold")
LogTextWidget.tag_configure("solved", foreground="#259020", font="helvetica 10 bold")
LogTextWidget.tag_configure("fail", foreground="#ff9900", font="helvetica 10 bold")


# Shooting Range
# ShootingFrame = tk.Frame(top, bd=5, relief=tk.RIDGE, padx=2, pady=2)
# ShootingFrame.place(x=100, y=500)
# b1 = tk.Button()

GreenDudeCanvas = tk.Canvas(top, height=200, width=400, bg='green4')
GreenDudeCanvas.place(x=25, y=525)
GreenDudePositions = []
for i in range(7):
    column = []
    for j in range(3):
        column.append((50*i + 30, 50*j+30, 50*i + 70, 50*j + 70))
    GreenDudePositions.append(column)
# print GreenDudePositions
GreenDudeCircles = []

# for column in GreenDudePositions:
#     for position in column:
#         GreenDudeCircles.append(GreenDudeCanvas.create_oval(*position, fill='red'))

correct = [2 - ((c + 1) % 256) for c in GreenDudeCorrectPassCode]
for i in range(7):
    column = []
    for j in range(3):
        if j == correct[i]:
            column.append(GreenDudeCanvas.create_oval(GreenDudePositions[i][j], outline='DodgerBlue4', width=3))
        else:
            column.append(GreenDudeCanvas.create_oval(GreenDudePositions[i][j], outline='green4', width=3))
    GreenDudeCircles.append(column)


def GreenDudeSetColors(positions):
    # print positions
    ps = [2 - ((c + 1) % 256) for c in positions]
    colors = ['yellow2', 'black', 'red']
    for i in range(min(7, len(ps))):
        for j in range(3):
            if j == ps[i]:
                GreenDudeCanvas.itemconfig(GreenDudeCircles[i][j], fill=colors[j])
            else:
                GreenDudeCanvas.itemconfig(GreenDudeCircles[i][j], fill="green4")

# TapeRecorderControls
TapeRecorderFrame = tk.Frame()
TapeRecorderPlayButton = tk.Button(TapeRecorderFrame, text="Play")
TapeRecorderPlayButton.pack()
TapeRecorderPauseButton = tk.Button(TapeRecorderFrame, text="Pause")
TapeRecorderPauseButton.pack()
TapeRecorderFrame.place(x=50, y=15)


NotifyQ = Queue.Queue()


def _notify():
    # print NotifyQ.qsize()
    while not NotifyQ.empty():
        (text, warning, solved, fail) = NotifyQ.get()
        text = "\n " + get_clock_text_now() + " -\t" + text
        LogTextWidget['state'] = 'normal'
        LogTextWidget.insert('end', text)
        LogTextWidget.see(tk.END)
        if warning:
            line = str(int(LogTextWidget.index("end").split('.')[0])-1)
            LogTextWidget.insert(line+".10", "WARNING: ")
            LogTextWidget.tag_add("warning", line+".10", line+".19")
            #print("notify: {}, tag=solved".format(line))

        if solved:
            line = str(int(LogTextWidget.index("end").split('.')[0])-1)
            LogTextWidget.insert(line+".10", "SOLVED: ")
            LogTextWidget.tag_add("solved", line+".10", line+".18")
            #print("notify: {}, tag=solved".format(line))

        if fail:
            line = str(int(LogTextWidget.index("end").split('.')[0])-1)
            LogTextWidget.insert(line+".10", "FAIL: ")
            LogTextWidget.tag_add("fail", line + ".9", line + ".16")
        LogTextWidget['state'] = 'disabled'
    top.after(100, _notify)


top.after(1000, _notify)


# Door Buttons
DoorButtonFrame = tk.Frame(top, bd=5, relief=tk.RIDGE, padx=2, pady=2)
DoorButtonFrame.place(x=1050, y=10)

door_button_callback = None

DoorNameList = ["Elevator", "Safe", "BookDrawer", "WineCaseHolder",
                "WineCase", "Stealth", "FromBomb", "FinalExit"]
DoorButtons = list()
for name in DoorNameList:
    b = tk.Button(DoorButtonFrame, text=name, bg='red', width=10)
    b.pack()
    DoorButtons.append(b)


# Mission Failures
MissionFailFrame = tk.Frame(top, bd=5, relief=tk.RIDGE, padx=2, pady=2)
MissionFailFrame.place(x=1200, y=10)
MissionFailButtons = []
for bname in FailButtonNames:
    b = tk.Button(MissionFailFrame, text=bname, width=15, state=tk.NORMAL)
    b.pack()
    MissionFailButtons.append(b)

# Hint Suggestion:
HintLoader = HintLoaderClass("hints.txt")
HintFrame = tk.Frame(top)
HintFrame.place(x=400, y=400)
HintButtons = []


def create_hint_buttons(hints):
    for button in HintButtons:
        button.destroy()
    del HintButtons[:]

    for hint in hints:
        button = tk.Button(HintFrame, text=hint)
        HintButtons.append(button)
        button.pack()
        button.bind("<Button-1>", hint_callback)


UpdateHints = False
Hints = None


def update_hints(key):
    global Hints
    global UpdateHints
    Hints = HintLoader.Hints[key]
    UpdateHints = True


def _update_hints():
    global UpdateHints
    if UpdateHints:
        create_hint_buttons(Hints)
        UpdateHints = False
    top.after(500, _update_hints)


top.after(500, _update_hints)


def hint_callback(event):
    button = event.widget
    text = button.config("text")[-1]
    SplitFlapEntry.delete(0., tk.END)
    SplitFlapEntry.insert(0., text)



# Next Up
NextUpFrame = tk.Frame(top)
NextUpFrame.place(x=800, y=500)
NextUpStaticLabel = tk.Label(NextUpFrame, text="Next up:", font="Verdana, 20 bold")
NextUpStaticLabel.pack()
NextUpInsideFrame = tk.Frame(NextUpFrame, bd=5, relief=tk.RIDGE, padx=2, pady=2)
NextUpInsideFrame.pack()
NextUpLabel = tk.Label(NextUpInsideFrame, text="The Pope needs to complete the initialization",
                       font="Verdana 14 bold")
NextUpLabel.pack()
NextUpQ = Queue.Queue()


def _next_up():
    if not NextUpQ.empty():
        text, bg = NextUpQ.get()
        NextUpLabel.configure(text=text)
        if bg == "red":
            NextUpLabel.configure(bg=bg)
        else:
            NextUpLabel.configure(bg=top.cget('bg'))
        NextUpInsideFrame.configure(bg=bg)
    top.after(500, _next_up)


top.after(1000, _next_up)


def next_up(text, bg="green"):
    NextUpQ.put((text, bg))

# Clock
ClockLabel = tk.Label(top, text="0:00:00", font="Verdana 28 bold")
ClockLabel.place(x=200, y=15)

import random

def test_nextup():
    text = random.choice(["sldfjsdjf", "jjerwoiewoipewroipewropiwe", "sdavclkmcvnmcvblojknnm", "5546ds6846546847"])
    bg = random.choice(["green", "red", "yellow"])
    next_up(text, bg)
    top.after(2000, test_nextup)

# top.after(3000, test_nextup)

def clock_make_text(sec):
    m, sec = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, sec)


def get_clock_text_now():
    if globals.ClockStartTime is None:
        return "00:00:00"
    displaytime = round(time.time() - globals.ClockStartTime)
    return clock_make_text(displaytime)


def update_clock(event=None):
    if globals.ClockHasStarted:
        ClockLabel.configure(text=get_clock_text_now())
    top.after(999, update_clock)

top.after(1000, update_clock)


# Handle Keyboard input
def keypress(event):
    # notify("you pressed key:" + event.char)
    return


def close_window(event):
    result = askquestion("Exit", "Are you sure you want to exit?", icon='warning')
    if result == 'yes':
        top.destroy()

top.bind("<Key>", keypress)
top.bind("<Escape>", close_window)


def nothing(event):
    print "doing nothing"
    top.after(500, nothing)


if __name__ == "__main__":
    print "Running interface as main"

    for action in Actions:
        ActionMenu.add_command(label=action)

    for submenu in DeviceSubmenus:
        submenu.add_command(label="example")

    GreenDudeSetColors([1, 1, 0, 0, 255, 255, 255])

    top.mainloop()
