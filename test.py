#!/usr/bin/env python3

import tkinter as tk

class Mainframe(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.frame = FirstFrame(self)
        self.frame.pack()

    def change(self, frame):
        self.frame.pack_forget() # delete currrent frame
        self.frame = frame(self)
        self.frame.pack() # make new frame

class FirstFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        master.title("Enter password")
        master.geometry("300x200")

        self.status = tk.Label(self, fg='red')
        self.status.pack()
        lbl = tk.Label(self, text='Enter password')
        lbl.pack()
        self.pwd = tk.Entry(self, show="*")
        self.pwd.pack()
        self.pwd.focus()
        self.pwd.bind('<Return>', self.check)
        btn = tk.Button(self, text="Done", command=self.check)
        btn.pack()
        btn = tk.Button(self, text="Cancel", command=self.quit)
        btn.pack()

    def check(self, event=None):
        if self.pwd.get() == 'password':
            self.master.change(SecondFrame)
        else:
            self.status.config(text="wrong password")

class SecondFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        master.title("Main application")
        master.geometry("600x400")

        lbl = tk.Label(self, text='You made it to the main application')
        lbl.pack()

if __name__=="__main__":
    app=Mainframe()
    app.mainloop()