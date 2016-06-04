from Tkinter import *
import time

import threading
import sys
import pyodbc

import matplotlib
matplotlib.use('TkAgg')
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure




class Window(Tk):

    def __init__(self,master):
        Tk.__init__(self,master)
        self.master = master
        self.FaceCZ()

    def FaceCZ(self):
        self.geometry("1000x600+30+30")

        self.graf = Figure(figsize=(8, 4), dpi=50)

        self.graf_canvas = FigureCanvasTkAgg(self.graf, master=self)

        self.graf_canvas.get_tk_widget().place(x = 10, y = 365)
        self.update_graf()

        #Bua til allt draslid:

       # self.button_START = Button(self, text = "START!", padx = 54, pady = 6, font = "Verdana 12 bold", command = self.Timer)
       # self.button_START.place(x = 330, y = 100)

        # Upplysingar um folkid
        self.title_Infomation = Label(self, text = "Infomation", font = "Verdana 12 bold")
        self.title_Infomation.place(x = 20, y = 20)

        self.text_Infomation = Text(self, width = 25, height = 6, wrap = WORD)
        self.text_Infomation.place(x = 20, y = 45)

        self.button_Infomation = Button(self, text = "Input", padx = 71, pady = 6) #command = self.Input
        self.button_Infomation.config(font = ("Verdana 12 bold"))
        self.button_Infomation.place(x = 20, y = 150)


        self.title_Timer = Label(text = "", font = "Verdana 28 bold")
        self.title_Timer.place(x = 330, y = 45)

        self.title_Task = Label(self, text = "Tasks" , font = "Verdana 12 bold")
        self.title_Task.place(x = 600, y = 20)

        self.text_Task = Text(self, width = 25, height = 33, wrap = WORD)
        self.text_Task.place(x = 600, y = 45)

        self.title_StartTime = Label(self, text = "Start \nTime", font = "Verdana 8 bold")
        self.title_StartTime.place(x = 820, y = 15)

        self.text_StartTime = Text(self, width = 6, height = 33, wrap = WORD)
        self.text_StartTime.place(x = 820, y = 45)


        self.title_EndTime = Label(self, text = "End \nTime", font = "Verdana 8 bold")
        self.title_EndTime.place(x = 900, y = 15)

        self.text_EndTime = Text(self, width = 6, height = 33, wrap = WORD)
        self.text_EndTime.place(x = 920, y = 45)


        self.title_Split_Flap = Label(self, text = "Split Flap", font = "Verdana 12 bold")
        self.title_Split_Flap.place(x = 20, y = 250)

        self.title_Split_Flap_current = Label(self, text = "Currently showing:", font = "Verdana 10 bold")
        self.title_Split_Flap_current.place(x = 20, y = 270)


        self.title_Split_Flap_Currently1 = Label(self, text = "", width = 2, borderwidth = 2, relief = "solid")
        self.title_Split_Flap_Currently1.place(x = 162, y = 270)

        self.title_Split_Flap_Currently2 = Label(self, text = "", width = 2, borderwidth = 2, relief = "solid")
        self.title_Split_Flap_Currently2.place(x = 180, y = 270)

        self.title_Split_Flap_Currently3 = Label(self, text = "", width = 2, borderwidth = 2, relief = "solid")
        self.title_Split_Flap_Currently3.place(x = 198, y = 270)

        self.title_Split_Flap_Currently4 = Label(self, text = "", width = 2, borderwidth = 2, relief = "solid")
        self.title_Split_Flap_Currently4.place(x = 225, y = 270)

        self.title_Split_Flap_Currently5 = Label(self, text = "", width = 2, borderwidth = 2, relief = "solid")
        self.title_Split_Flap_Currently5.place(x = 243, y = 270)

        self.title_Split_Flap_Currently6 = Label(self, text = "", width = 2, borderwidth = 2, relief = "solid")
        self.title_Split_Flap_Currently6.place(x = 261, y = 270)

        self.title_Split_Flap_Hint = Label(self, text = "Hint:", font = "Verdana 12 bold")
        self.title_Split_Flap_Hint.place(x = 20, y = 300)

        self.text_Split_Flap_Hint_Next = Entry(self, width = 6)
        self.text_Split_Flap_Hint_Next.place(x = 75, y = 303)
        self.text_Split_Flap_Hint_Next.insert(END, " ")

        self.button_Split_Flap_Hint_Submit = Button(self, text = "Submit", padx = 1, pady = 1, command = self.submit_hint)
        self.button_Split_Flap_Hint_Submit.place(x = 150, y = 300)

        self.title_Split_Flap_Hint_Custom = Label(self, text = "Give custom Hint:", font = "Verdana 12 bold")
        self.title_Split_Flap_Hint_Custom.place(x = 20, y = 330)

        self.text_Split_Flap_Hint_Custom = Entry(self, width = 6)
        self.text_Split_Flap_Hint_Custom.place(x = 180, y = 333)

        self.button_Split_Flap_Hint_Custom_Submit = Button(self, text = "Submit", padx =1, pady = 1, command = self.submit_hint_custom)
        self.button_Split_Flap_Hint_Custom_Submit.place(x = 250, y = 330)


        self.title_Timer.configure(text = "0:00:00")
        self.task_window()




        self.text_Task.tag_configure('Done', foreground = "gray", font = ('TkDefaultFont',12), spacing1 = 5)
        self.text_Task.tag_configure('During', font = ('TkDefaultFont',12, 'bold'), spacing1 = 5)
        self.text_Task.tag_configure('After', foreground = "blue", font =('TkDefaultFont', 12), spacing1 = 5)

        self.text_StartTime.tag_configure('text', font =('TkDefaultFont', 12, 'bold'), spacing1 = 5)
        #self.update_task_window(None,None)


    starttime = None
    split_flap_input = None
    Duration = list()

    @staticmethod
    def reikna_tima_h(sec):
        m,sec = divmod(sec,60)
        h,m = divmod(m,60)
        return "%d:%02d:%02d" % (h,m,sec)

    @staticmethod
    def reikna_tima_m(sec):
        m,sec = divmod(sec,60)
        h,m = divmod(m,60)
        return "%02d:%02d" % (m,sec)

    def update_clock(self):
        displaytime = round(time.time() - self.starttime)
        self.title_Timer.configure(text = self.reikna_tima_h(displaytime))
        self.after(1000, self.update_clock)

    def Split_flap_update(self):
        self.title_Split_Flap_Currently1.configure(text = self.Split_flap_input[0])
        self.title_Split_Flap_Currently2.configure(text = self.Split_flap_input[1])
        self.title_Split_Flap_Currently3.configure(text = self.Split_flap_input[2])
        self.title_Split_Flap_Currently4.configure(text = self.Split_flap_input[3])
        self.title_Split_Flap_Currently5.configure(text = self.Split_flap_input[4])
        self.title_Split_Flap_Currently6.configure(text = self.Split_flap_input[5])


    def task_window(self):
        self.text_Task.config(state = NORMAL)
        for t in tasks:
            self.text_Task.insert(END, t.Name + "\n", 'After')
        self.text_Task.config(state = DISABLED)


    def update_task_window(self, current_number, duration):
        # Update Taks window
        self.text_Task.config(state=NORMAL)
        self.text_Task.delete(0.0, END)
        self.text_Split_Flap_Hint_Next.config(state = NORMAL)
        self.text_Split_Flap_Hint_Next.delete(0, END)
        for t in tasks:
            if t.Number < current_number:
                self.text_Task.insert(END,t.Name + "\n", 'Done')
            elif t.Number == current_number:
                self.text_Task.insert(END,t.Name + "\n", 'During')
                self.text_Split_Flap_Hint_Next.insert(END, t.Hint)
            else:
                self.text_Task.insert(END, t.Name + "\n", 'After')

        self.text_Split_Flap_Hint_Next.config(state = DISABLED)
        self.text_Task.config(state=DISABLED)

        # Update Start time Window
        self.text_StartTime.config(state = NORMAL)
        self.text_StartTime.delete(0.0, END)
        self.text_EndTime.config(state = NORMAL)
        self.text_EndTime.delete(0.0, END)
        if duration != None:
            for i in range(len(duration)):
                self.text_StartTime.insert(END,self.reikna_tima_m(duration[i]-self.starttime)+"\n", 'text')
                if i > 0:
                    self.text_EndTime.insert(END,self.reikna_tima_m(duration[i]-self.starttime) + "\n", 'text')
        self.text_StartTime.config(state = DISABLED)
        self.text_EndTime.config(state = DISABLED)

    def update_graf(self):
        a = self.graf.add_subplot(111)
        t = arange(0.0, 3.0, 0.01)
        s = t

        a.plot(t, s)
        self.graf_canvas.show()


    def submit_hint(self):
        send2POPE("5:" + self.text_Split_Flap_Hint_Next.get())

    def submit_hint_custom(self):
        Hint = self.text_Split_Flap_Hint_Custom.get()
        if len(Hint) > 6:
            self.text_Split_Flap_Hint_Custom.delete(0, END)
            self.text_Split_Flap_Hint_Custom.insert(END, "2 long")
        else:
            self.text_Split_Flap_Hint_Custom.delete(0,END)
            send2POPE("5:" + Hint)

class Task:
    task_starttime = None
    taks_endtime = None
    taks_duration = None
    def __init__(self, name, avgduration, hint, number):
        self.Name = name
        self.Avgduration = avgduration
        self.Hint = hint
        self.Number = number



# Populate events from database
tasks = list()
# cnxn = pyodbc.connect(r'Driver={SQL Server};'
#                       r'Server=.\SQLEXPRESS;'
#                       r'Database=KjallariDB;'
#                       r'Trusted_Connection=yes;')
# cursor = cnxn.cursor()
# cursor.execute("SELECT [Name],[AVGDuration],[Hint],[Number] FROM [dim_Tasklist] WHERE [Number] IS NOT null ORDER BY [Number]")
# while True:
#     row = cursor.fetchone()
#     if not row:
#         break
#     else:
#         tasks.append(Task(row.Name, row.AVGDuration, row.Hint, row.Number))
# cnxn.close()

stdoutLock = threading.Lock()
def send2POPE(output):
    with stdoutLock:
        sys.stdout.write(output + "\n")

class _Event:
    def __init__(self, _id, name, react_fun):
        self.React_fun = react_fun
        self.ID = _id
        self.Name = name

    def fire(self, incoming=None):
        self.React_fun(incoming)


# This static class was created to hold all reactions without clustering the global namespace
class Reactions:
    def __init__(self):
        pass

#   All Reactions must be defined here
    @staticmethod
    def no_reaction():
        pass

    @staticmethod
    def execute(incoming):
        exec incoming

    @staticmethod
    def test(incoming):
        print "Reactions.test recieved the message:  " + incoming

    @staticmethod
    def startclock(incoming):
        window.starttime = float(incoming)
        window.update_clock()

    @staticmethod
    def splitflap(incoming):
        window.Split_flap_input = incoming
        if len(window.Split_flap_input)<6:
            b = 6-len(window.Split_flap_input)
            for i in range(b):
                window.Split_flap_input = window.Split_flap_input + " "

        window.Split_flap_update()



    @staticmethod
    def Task_breytist(incoming):
        breyta = incoming.split(";")
        Task_number = int(breyta[0])
        window.Duration.append(float(breyta[1]))
        print window.Duration
        window.update_task_window(Task_number, window.Duration)


events = list()
#herna tarf ad skilgreina events med:
events.append(_Event(1, "Test", Reactions.test))
events.append(_Event(2,"KLukkaFerIgang", Reactions.startclock))
events.append(_Event(3,"SplitflapInfo",Reactions.splitflap))
events.append(_Event(4,"TakskBreytist", Reactions.Task_breytist))
events.append(_Event(100,"Execute",Reactions.execute))





class FireEventThread(threading.Thread):
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming

    def run(self):
        event = self.Incoming.split(':')
        for e in events:
            if e.ID == int(event[0]):
                e.fire(event[1][:-1])



class ListeningThread(threading.Thread):
    def __init__(self, listen2):
        threading.Thread.__init__(self)
        self.listen2 = listen2

    def run(self):
        while True:
            incoming = self.listen2.readline()
            fire = FireEventThread(incoming)
            fire.start()

Asgeir = ListeningThread(sys.stdin)
Asgeir.start()

window = Window(None)

window.title("Camp Z")

window.mainloop()

