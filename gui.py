import tkinter as tk

import requests
import json
import time

from book import Book, Library
from fields import fields
from timer import Timer

from isbn import get_data, ask_book, fetch
from barscan import get_barcode, get_pic, test_ip

from PIL import Image, ImageTk


def quit(process):
    process.destroy()


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.pack()

        self.frames = {}

        self.fields = ('Variable 1', 'Variable 2', 'Variable 3', 'Variable 4', 'Variable 5')
        #self.defaults = ('Default 1', 'Default 2', 'Default 3')

        self.frames['left'] = tk.Frame(self.master)
        self.frames['left'].pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        self.frames['right'] = tk.Frame(self.master)
        self.frames['right'].pack(side = tk.RIGHT, expand = tk.YES, fill = tk.BOTH)

        self.frames['buttons1'] = tk.Frame(self.frames['left'])
        self.frames['buttons1'].pack(side = tk.TOP, expand = tk.YES, fill = tk.X)

        self.buttons = {}

        self.buttons['exit'] = tk.Button(self.frames['buttons1'], text="Exit", command=lambda e=self.master: quit(e))
        self.buttons['exit'].pack(side=tk.LEFT)

        self.buttons['prev'] = tk.Button(self.frames['buttons1'], text="<")
        self.buttons['next'] = tk.Button(self.frames['buttons1'], text=">")
        self.buttons['prev'].pack(side=tk.LEFT)
        self.buttons['next'].pack(side=tk.LEFT)
        self.buttons['idEnt'] = tk.Entry(self.frames['buttons1'], text="1")
        self.buttons['idLab'] = tk.Label(self.frames['buttons1'], text="Size")
        self.buttons['idBut'] = tk.Button(self.frames['buttons1'], text='Go')
        self.buttons['idEnt'].pack(side=tk.LEFT)
        self.buttons['idLab'].pack(side=tk.LEFT)
        self.buttons['idBut'].pack(side=tk.LEFT)

        self.frames['fields'] = tk.Frame(self.frames['left'])
        self.frames['fields'].pack(side = tk.TOP, expand = tk.YES, fill = tk.BOTH)

        self.entries = self.makeform(self.frames['left'], self.fields)

        self.frames['buttons2'] = tk.Frame(self.frames['left'])
        self.frames['buttons2'].pack(side=tk.BOTTOM, expand = tk.YES, fill =tk.X)

        self.buttons['save'] = tk.Button(self.frames['buttons2'], text="Save", command=lambda e = self.entries: self.collect(e))
        self.buttons['save'].pack(side=tk.TOP, fill=tk.X, padx=20)

        self.frames['buttons3'] = tk.Frame(self.frames['right'])
        self.frames['buttons3'].pack(side=tk.TOP, expand = tk.YES, fill = tk.X)


        self.buttons['mode'] = tk.Button(self.frames['buttons3'], text="Initial", command=self.toggleMode)
        self.buttons['mode'].pack(side=tk.TOP, fill=tk.X)

        #self.entryip = self.makeform(self.frames['buttons3'], ('Camera IP',)).get('Camera IP')
        #self.entryip.bind('<Enter>', lambda e=None: self.connect())
        self.buttons['ipEnt'], self.buttons['ipBut'] = self.entrybutton(self.frames['buttons3'], 'Camera IP', 'Go', self.toggleConnection)
        self.info = tk.Label(self.frames['buttons3'], text="Initial")
        self.info.pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE)

        #self.frames['screen'] = tk.Frame(self.frames['right'])

        #self.frames['screen'] = Screen(tk.Tk())
        #self.frames['screen'].pack(side=tk.TOP, expand = tk.YES, fill = tk.BOTH)

        self.connected = False
        self.mode = 1
        self.toggleMode()


    def test(self, e):
        e.configure(cnf={'text': '!'})


    def makeform(self, master, fields, defaults=None):
        entries = {}
        defaults = defaults or tuple(None for el in fields)
        for field, default in zip(fields, defaults):
            row = tk.Frame(master)
            lab = tk.Label(row, width=22, text=field+": ", anchor='w')
            ent = tk.Entry(row)
            if default:
                ent.insert(0, default)
            row.pack(side = tk.TOP, fill = tk.X, padx = 10 , pady = 5)
            lab.pack(side = tk.LEFT)
            ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
            entries[field] = ent
        return entries

    def entrybutton(self, master, field_name, button_name, button_command, default=None):
        row = tk.Frame(master)
        lab = tk.Label(row, width=12, text=field_name+": ", anchor='w')
        ent = tk.Entry(row)
        if default:
            ent.insert(0, default)
        but = tk.Button(row, text=button_name, command=button_command)
        row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 5)
        lab.pack(side = tk.LEFT)
        ent.pack(side = tk.LEFT, expand=tk.YES, fill = tk.X)
        but.pack(side = tk.RIGHT)
        return (ent, but)


    def collect(self, entries):
        for key, entry in entries.items():
            print('{}: {}'.format(key, entry.get()))


    def toggleMode(self):
        if self.mode == 0:
            self.modeEdit()
        else:
            self.modeAdd()

    def modeAdd(self):
        self.mode = 0
        self.info['text'] = 'Enter camera IP and click Go'
        self.buttons['ipEnt']['state'] = 'normal'
        self.buttons['ipBut']['text'] = 'Go'
        self.buttons['mode']['text'] = 'ADD'
        self.connected = False


    def modeEdit(self):
        self.mode = 1
        self.info['text'] = 'Edit mode'
        self.buttons['ipEnt']['state'] = 'disabled'
        self.buttons['ipBut']['text'] = ''
        self.buttons['mode']['text'] = 'EDIT'
        self.screen = None
        self.connected = False

    def toggleConnection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()


    def connect(self):
        self.info['text'] = 'Connecting...'
        self.ip = self.buttons['ipEnt'].get()
        if test_ip(self.ip):
            self.info['text'] = 'Camera online'
            self.buttons['ipBut']['text'] = 'ON'
            self.screen = tk.Toplevel()
            self.connected = True
        else:
            self.info['text'] = 'Invalid IP. Please retry'


    def disconnect(self):
        self.info['text'] = 'Camera offline'
        self.buttons['ipBut']['text'] = 'OFF'
        self.screen = None
        self.connected = False


    def refresh(self):
        import matplotlib.pyplot as plt
        if self.mode == 0 and self.connected:
            self.array = get_pic(ip=self.ip)
            self.load = Image.fromarray(self.array)
            self.render = ImageTk.PhotoImage(self.load)

            image = tk.Label(self.screen, image=self.render)
            image.place(x=0, y=0)


class Screen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.pack()



if __name__ == '__main__':

    root = tk.Tk()
    myapp = App(root)

    while True:

        try:
            myapp.update()
            myapp.refresh()
        except (KeyboardInterrupt, tk.TclError):
            break
        time.sleep(.2)


        