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
frmbgd = "lightsteelblue4" #Backgroundcolor


top = tk.Tk()
# top.attributes("-fullscreen", True)
top.geometry("1400x1200")
top.configure(bg=frmbgd)
top.title('The Pope 1.1')

frmbgd = "light slate gray"   # Background colour

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
    "Stealth Finish",
    "Start TimeBomb",
    "ElevatorHint 1",
    "ElevatorHint 2",
    "ElevatorHint 3",
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

        PlayersFrame.config(background="goldenrod")
        PlayersLabel.config(background="goldenrod")
        PlayersLabel1.config(background="goldenrod")
        NumberOfPlayersLabel.config(bg="goldenrod", fg="white", text=ret_player_info["NofPlayers"])

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


#Action buttons
ActionButtonFrame = tk.Frame(width=50, background="goldenrod")
ActionButtons = []

ActionButtonLabel = tk.Label(ActionButtonFrame, background="goldenrod", text="Main Actions", font="Verdana, 10 bold", pady=8)
ActionButtonLabel.pack()

ActionButtonCheckDevice = tk.Button(ActionButtonFrame,text="Check All Device Status")
ActionButtonCheckDevice.pack()

ActionButtonNewGroup = tk.Button(ActionButtonFrame, text="New Group")
ActionButtonNewGroup.pack()

ActionButtonEditGroup = tk.Button(ActionButtonFrame, text="Edit Group")
ActionButtonEditGroup.pack()

# ActionButtonEditGroup = tk.Button(ActionButtonFrame, text="Reset Room")
# ActionButtonEditGroup.pack()

ActionButtonShootingRangeRegisterHit = tk.Button(ActionButtonFrame, text="Register Hit!")
ActionButtonShootingRangeRegisterHit.pack()

ActionButtons.append(ActionButtonCheckDevice)
ActionButtons.append(ActionButtonNewGroup)
ActionButtons.append(ActionButtonEditGroup)
ActionButtons.append(ActionButtonShootingRangeRegisterHit)

ActionButtonFrame.place(x=10, y=120)

PlayersFrame = tk.Frame(width=100, background="red")
PlayersFrame.pack()
PlayersFrame.place(x=200, y=120)
PlayersLabel = tk.Label(PlayersFrame, background="red", text="Players Info", font="Verdana, 14 bold", pady=8)
PlayersLabel.pack()
PlayersLabel1 = tk.Label(PlayersFrame, background="red", text="Number of Players:", font="Verdana, 10 bold")
PlayersLabel1.pack()
NumberOfPlayersLabel = tk.Label(PlayersFrame, bg="red", fg="white", text="Unknown",
                       font="Verdana 10 bold")
NumberOfPlayersLabel.pack()



# ActionButtons = tk.Frame(top, bd=5, relief=tk.RIDGE, padx=2, pady=2)

DeviceMenu = tk.Menu(Menu, tearoff=False)
Menu.add_cascade(label="Devices", menu=DeviceMenu)
for device in Devices:
    submenu = tk.Menu(DeviceMenu, tearoff=False)
    DeviceMenu.add_cascade(label=device, menu=submenu)
    DeviceSubmenus.append(submenu)


# SplitFlap
# SplitFlapEntryFrame = tk.Frame(relief=tk.RIDGE)
# SplitFlapEntryFrame.place(x=10, y=130)
# SplitFlapEntryFrame.pack()
SplitFlapLabel = tk.Label(text="Splitflap Hint Text:",fg="white", font="Verdana, 10 bold", background="lightsteelblue4")
SplitFlapLabel.place(x=15, y=300)
SplitFlapEntry = tk.Text(bd=3, width=20, height=5, font="Verdana 16")
SplitFlapEntry.place(x=15, y=330)
SplitFlapEntryButton = tk.Button(top, bg="green", text="Send hint")
SplitFlapEntryButton.place(x=325, y=340)
SplitFlapEntryClearButton = tk.Button(top, text="Clear")
SplitFlapEntryClearButton.place(x=325, y=380)
SplitFlapDisplayLabel = tk.Label(top,
                                 text="Now displaying: '           '",
                                 fg="white", font="Verdana 12 bold", background="lightsteelblue4"
                                 )
SplitFlapDisplayLabel.place(x=15, y=480)


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
ProgressPlotCanvas.get_tk_widget().place(x=25, y=700)


def update_progress_plot(times):
    ProgressPlotFigure.clear()
    p = ProgressPlotFigure.add_subplot(111)
    p.plot(range(11), ProgressPlotBaseLine, color="r")
    print "plot times: {}".format(times)
    p.plot(range(len(times)), times)
    ProgressPlotCanvas.draw()



# Log Text
LogTextWidget = tk.Text(top, height=25, width=60, font="helvetica 12")
LogTextWidget.place(x=450, y=25)
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
GreenDudeCanvas.place(x=25, y=875)
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
TapeRecorderFrame = tk.Frame(background="lightblue3")
TapeRecorderLabel= tk.Label(TapeRecorderFrame, background="lightblue3", text="TapeRec Actions", font="Verdana, 10 bold", pady=8)
TapeRecorderLabel.pack()
TapeRecorderPlayButton = tk.Button(TapeRecorderFrame, text="Play")
TapeRecorderPlayButton.pack()
TapeRecorderPauseButton = tk.Button(TapeRecorderFrame, text="Pause")
TapeRecorderPauseButton.pack()
TapeRecorderFrame.place(x=10, y=20)


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
NextUpFrame = tk.Frame(top, background="yellow2")
NextUpFrame.place(x=500, y=550)

NextUpStaticLabel = tk.Label(NextUpFrame, text="Next up:", font="Verdana, 20 bold", bg="yellow2")
NextUpStaticLabel.pack()
NextUpInsideFrame = tk.Frame(NextUpFrame, bd=5, relief=tk.RIDGE, padx=2, pady=2, bg="white")
NextUpInsideFrame.pack()
NextUpLabel = tk.Label(NextUpInsideFrame, bg="azure2", text="The Pope needs to complete the initialization",
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


# Resend

ResendButton = tk.Button(top, bg="OrangeRed2", text="\n    Resend!!!    \n", font="Verdana 28 bold")
ResendButton.place(x=500, y=900)


def _resend_callback(event):
    ResendButton.config(state=tk.DISABLED)

ResendButton.bind("<Button-1>", _resend_callback)


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
