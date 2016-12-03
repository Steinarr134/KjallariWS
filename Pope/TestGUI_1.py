import Tkinter as tk


top = tk.Tk()


def nothing(event=None):
    print "nothing happened"


top.after(500, nothing)

top.mainloop()
