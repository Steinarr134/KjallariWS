import Tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import Queue
InitWindow = tk.Tk()
top = tk.Tk()
top.attributes("-fullscreen", True)

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

ProgressPlot = Figure(figsize=(8, 4), dpi=100)
ProgressPlotCanvas = FigureCanvasTkAgg(ProgressPlot, master=top)
ProgressPlotCanvas.get_tk_widget().place(x=1050, y=700)


class StdoutRedirector(object):
    def __init__(self,text_widget, root):
        self.text_space = text_widget
        self.Q = Queue.Queue()
        self.root = root
        self.root.after(100, self.check_on_queue)

    def write(self, string):
        print "something put into Q"
        self.Q.put(string)

    def check_on_queue(self, event=None):
        print "checking on Q"
        if not self.Q.empty():
            string = self.Q.get()
            self.text_space.insert('end', string)
            self.text_space.see('end')
        self.root.after(100, self.check_on_queue)

LogTextWidget = tk.Text(top, height=29, width=135)
LogTextWidget.place(x=50, y=700)

##sys.stderr = StdoutRedirector(LogTextWidget, top)

DoorButtonFrame = tk.Frame(top, bd=5, relief=tk.RIDGE, padx=2, pady=2)
DoorButtonFrame.place(x=1050, y=100)

door_button_callback = None

DoorNameList = ["Elevator", "Safe"]
DoorButtons = list()
for name in DoorNameList:
    b = tk.Button(DoorButtonFrame, text=name, bg='red', width=10)
    b.pack()
    DoorButtons.append(b)


ClockLabel = tk.Label(top, text="0:00:00", font="Verdana 28 bold")
ClockLabel.place(x=350, y=50)
ClockHasStarted = False
ClockStartTime = None


def clock_make_text(sec):
    m,sec = divmod(sec,60)
    h,m = divmod(m,60)
    return "%d:%02d:%02d" % (h,m,sec)


def update_clock(event=None):
    if ClockHasStarted:
        displaytime = round(time.time() - ClockStartTime)
        self.title_Timer.configure(text = clock_make_text(displaytime))
        top.after(1000, update_clock)

top.after(1000, update_clock)


def keypress(event):
    print "you pressed key:" + event.char


def close_window(event):
    top.destroy()

top.bind("<Key>", keypress)
top.bind("<Escape>", close_window)


def nothing(event):
    print "doing nothing"
    top.after(500, nothing)




print "sdflsdkfj"


if __name__ == "__main__":
    top.mainloop()
    print "kkkkkkkk"



