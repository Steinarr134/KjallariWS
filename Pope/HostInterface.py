
import Tkinter as tk
top = tk.Tk()
top.attributes("-fullscreen", True)

SplitFlapEntry = tk.Entry(top, bd=5)
SplitFlapEntry.place(x=50, y=100)

SplitFlapEntryButton = tk.Button(top, text="Send hint")
SplitFlapEntryButton.place(x=230, y=100)

##top.mainloop()

