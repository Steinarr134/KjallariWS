import Tkinter as tk
from tkMessageBox import askquestion
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
from Config import *

# Possibly Persistant values
class P(object):
    def __init__(self):
        self.ClockHasStarted = False
        self.ClockStartTime = None


o = P()


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
        window.destroy()
        # top.deiconify()
        ret_player_info = {"NofPlayers": 3,
                           "more info": "some info"}
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
SplitFlapDisplayLabel = tk.Label(top,
                                 text="Now displaying: '           '",
                                 font="Verdana 12 bold")
SplitFlapDisplayLabel.place(x=50, y=250)


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
ProgressPlot = Figure(figsize=(8, 4), dpi=50)
ProgressPlotCanvas = FigureCanvasTkAgg(ProgressPlot, master=top)
ProgressPlotCanvas.get_tk_widget().place(x=25, y=300)


# Log Text
LogTextWidget = tk.Text(top, height=20, width=75, font="helvetica 10")
LogTextWidget.place(x=550, y=225)
LogTextWidget.insert('end', " System starting...")
LogTextWidget['state'] = 'disabled'
LogTextWidget.tag_configure("warning", foreground="#ff0000", font="helvetica 10 bold")
LogTextWidget.tag_configure("solved", foreground="#259020", font="helvetica 10 bold")
LogTextWidget.tag_configure("fail", foreground="#ff9900", font="helvetica 10 bold")


# Shooting Range
# ShootingFrame = tk.Frame(top, bd=5, relief=tk.RIDGE, padx=2, pady=2)
# ShootingFrame.place(x=100, y=500)
# b1 = tk.Button()

ShootingCanvas = tk.Canvas(top, height=200, width=200, bg='blue')
ShootingCanvas.place(x=550, y=10)
ShootingPositions = [
    (135, 135, 195, 195),
    (5, 135, 65, 195),
    (5, 5, 65, 65),
    (70, 70, 130, 130),
    (135, 5, 195, 65)
]
ShootingCircles = []
for position in ShootingPositions:
    ShootingCircles.append(ShootingCanvas.create_oval(*position, fill='red'))
# c2 = ShootingCanvas.create_oval()


def ShootingCirclesSetColor(n, color):
    ShootingCanvas.itemconfig(ShootingCircles[n], fill=color)

# TapeRecorderControls
TapeRecorderFrame = tk.Frame()
TapeRecorderPlayButton = tk.Button(TapeRecorderFrame, text="Play")
TapeRecorderPlayButton.pack()
TapeRecorderPauseButton = tk.Button(TapeRecorderFrame, text="Pause")
TapeRecorderPauseButton.pack()
TapeRecorderFrame.place(x=100, y=15)


def notify(text, warning=False, solved=False, fail=False):
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
        LogTextWidget.tag_add("fail", line+".9", line+".16")
    LogTextWidget['state'] = 'disabled'


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
MissionFailFrame.place(x=850, y=10)
MissionFailButtons = []
for bname in FailButtonNames:
    b = tk.Button(MissionFailFrame, text=bname, width=15, state=tk.NORMAL)
    b.pack()
    MissionFailButtons.append(b)


# Clock
ClockLabel = tk.Label(top, text="0:00:00", font="Verdana 28 bold")
ClockLabel.place(x=350, y=50)


def clock_make_text(sec):
    m, sec = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, sec)


def get_clock_text_now():
    if o.ClockStartTime is None:
        return "00:00:00"
    displaytime = round(time.time() - o.ClockStartTime)
    return clock_make_text(displaytime)


def update_clock(event=None):
    if o.ClockHasStarted:
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
        submenu.add_command(label="GetStatus")

    top.mainloop()
