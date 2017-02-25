import Tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import Queue
import time

top = tk.Tk()
top.attributes("-fullscreen", True)
top.withdraw()

# Init Window
InitWindow = tk.Tk()
#InitWindow.withdraw()
AboutPlayersEntry = tk.Text(InitWindow, bd=5, width=20, height=5, font="Verdana16")
AboutPlayersEntry.pack()
AboutPlayersSubmitButton = tk.Button(InitWindow, text="Submit")
AboutPlayersSubmitButton.pack()
def exit_init_window(event=None):
    # send info too database
    InitWindow.destroy()
    top.deiconify()
AboutPlayersSubmitButton.bind("<Button-1>", exit_init_window)

SplitFlapEntry = tk.Text(top, bd=5, width=20, height=5, font="Verdana 16")
SplitFlapEntry.place(x=50, y=100)

SplitFlapEntryButton = tk.Button(top, text="Send hint")
SplitFlapEntryButton.place(x=230, y=100)




def fix_split_flap_input(event=None):
##    print "'" + event.char + "'"
    if event.char:
        stuff = SplitFlapEntry.get(1.0, tk.END)
##        print stuff.split('\n')
        last_part = stuff.split('\n')[-2]
##        print "len: " + str(len(last_part))
        if len(last_part) > 10:
            SplitFlapEntry.insert(float(len(stuff)), '\n')

SplitFlapEntry.bind("<Key>", fix_split_flap_input)
SplitFlapEntry.bind("<BackSpace>", lambda event: None)

ProgressPlot = Figure(figsize=(8, 4), dpi=50)
ProgressPlotCanvas = FigureCanvasTkAgg(ProgressPlot, master=top)
ProgressPlotCanvas.get_tk_widget().place(x=25, y=250)


LogTextWidget = tk.Text(top, height=20, width=75)
LogTextWidget.place(x=600, y=300)
LogTextWidget.insert('end', " System starting...")
LogTextWidget['state'] = 'disabled'

def notify(text):
    text = "\n " + get_clock_text_now() + " - " + text
    LogTextWidget['state'] = 'normal'
    LogTextWidget.insert('end', text)
    LogTextWidget.see(tk.END)
    LogTextWidget['state'] = 'disabled'


##sys.stderr = StdoutRedirector(LogTextWidget, top)

DoorButtonFrame = tk.Frame(top, bd=5, relief=tk.RIDGE, padx=2, pady=2)
DoorButtonFrame.place(x=1050, y=10)

door_button_callback = None

DoorNameList = ["Elevator", "Safe", "BookDrawer", "WineCaseHolder",
                "Stealth", "FromBomb", "FinalExit"]
DoorButtons = list()
for name in DoorNameList:
    b = tk.Button(DoorButtonFrame, text=name, bg='red', width=10)
    b.pack()
    DoorButtons.append(b)

MissionFailFrame = tk.Frame(top, bd=5, relief=tk.RIDGE, padx=2, pady=2)
MissionFailFrame.place(x=850, y=10)
MissionFailButtons = [
    tk.Button(MissionFailFrame, text="Elevator Escape", width=15),
    tk.Button(MissionFailFrame, text="Start TapeRecorder", width=15),
    tk.Button(MissionFailFrame, text="Open Safe", width=15),
    tk.Button(MissionFailFrame, text="GreenDude Fail", width=15),
    tk.Button(MissionFailFrame, text="Start Lie Detector", width=15),
    tk.Button(MissionFailFrame, text="Morse Fail", width=15),
]
for b in MissionFailButtons:
    b.pack()


ClockLabel = tk.Label(top, text="0:00:00", font="Verdana 28 bold")
ClockLabel.place(x=350, y=50)
ClockHasStarted = False
ClockStartTime = None


def clock_make_text(sec):
    m,sec = divmod(sec,60)
    h,m = divmod(m,60)
    return "%d:%02d:%02d" % (h,m,sec)


def get_clock_text_now():
    displaytime = round(time.time() - ClockStartTime)
    return clock_make_text(displaytime)


def update_clock(event=None):
    if ClockHasStarted:
        ClockLabel.configure(text=get_clock_text_now())
    top.after(999, update_clock)

top.after(1000, update_clock)


def keypress(event):
##    notify("you pressed key:" + event.char)
    return


def close_window(event):
    top.destroy()

top.bind("<Key>", keypress)
top.bind("<Escape>", close_window)


def nothing(event):
    print "doing nothing"
    top.after(500, nothing)





if __name__ == "__main__":
    top.mainloop()
    print "kkkkkkkk"



