import tkinter as tk

import requests
import json
import time

from .context import Book, Library, fields, Timer, get_data, ask_book, fetch, \
    get_barcode, get_pic, ask_url

from PIL import Image, ImageTk


def quit(process):
    process.destroy()


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.pack()

        self.frames = {}
        self.buttons = {}
        self.labels = {}
        self.entries = {}
        self.info = {}

        self.fields_data = ['ISBN', 'Title', 'Author', 'Publisher', 'Subjects']
        self.fields_location = ['Room', 'Module', 'Shelf']
        #self.defaults = ('Default 1', 'Default 2', 'Default 3')

        self.frames['left'] = tk.Frame(self.master)
        self.frames['left'].pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        self.frames['right'] = tk.Frame(self.master)
        self.frames['right'].pack(side = tk.RIGHT, expand = tk.YES, fill = tk.BOTH)

        self.frames['buttons12'] = tk.Frame(self.frames['right'])
        self.frames['buttons12'].pack(side = tk.BOTTOM, expand = tk.YES, fill = tk.X)
        self.frames['buttons11'] = tk.Frame(self.frames['right'])
        self.frames['buttons11'].pack(side = tk.BOTTOM, expand = tk.YES, fill = tk.X)

        self.buttons['prev'] = tk.Button(self.frames['buttons11'], text="◀", command=self.navPrev)
        self.buttons['next'] = tk.Button(self.frames['buttons11'], text="▶", command=self.navNext)
        self.buttons['first'] = tk.Button(self.frames['buttons11'], text="◀◀", command=self.navFirst)
        self.buttons['last'] = tk.Button(self.frames['buttons11'], text="▶▶", command=self.navLast)
        self.buttons['first'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.buttons['prev'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.buttons['next'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.buttons['last'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.labels['form'] = tk.Label(self.frames['buttons12'], text="Form: ")
        self.buttons['idEnt'] = tk.Entry(self.frames['buttons12'])
        self.buttons['idLab'] = tk.Label(self.frames['buttons12'], text="/Size")
        self.buttons['idBut'] = tk.Button(self.frames['buttons12'], text='Go', command=self.navInput)
        self.labels['form'].pack(side=tk.LEFT)
        self.buttons['idEnt'].pack(side=tk.LEFT)
        self.buttons['idLab'].pack(side=tk.LEFT)
        self.buttons['idBut'].pack(side=tk.LEFT)
        self.buttons['exit'] = tk.Button(self.frames['buttons12'], text="Exit", command=lambda e=self.master: quit(e))
        self.buttons['exit'].pack(side=tk.LEFT)

        self.frames['fields'] = tk.Frame(self.frames['left'])
        self.frames['fields'].pack(side = tk.TOP, expand = tk.YES, fill = tk.BOTH)

        loc_row = tk.Frame(self.frames['fields'])
        loc_row.pack(side=tk.TOP, expand=tk.YES, fill =tk.X)
        for field in self.fields_location:
            self.addentry(loc_row, field, width_label=8, width_entry=5, multiple=True)

        self.entries['isbn'], self.buttons['isbnBut'] = self.entrybutton(self.frames['fields'], 'ISBN', 'Search', self.isbnGo)
        for field in self.fields_data[1:]:
            self.addentry(self.frames['fields'], field)
        #self.makeform(self.frames['left'], self.fields_data)

        self.frames['buttons2'] = tk.Frame(self.frames['left'])
        self.frames['buttons2'].pack(side=tk.BOTTOM, expand = tk.YES, fill =tk.X)

        self.buttons['save'] = tk.Button(self.frames['buttons2'], text="Save", command=self.save)
        self.buttons['save'].pack(side=tk.LEFT, fill=tk.X, padx=5, expand=tk.YES)
        self.buttons['restore'] = tk.Button(self.frames['buttons2'], text="Restore", command=self.restore)
        self.buttons['restore'].pack(side=tk.RIGHT, fill=tk.X, padx=5, expand=tk.YES)


        self.frames['buttons3'] = tk.Frame(self.frames['right'])
        self.frames['buttons3'].pack(side=tk.TOP, expand = tk.YES, fill = tk.X)


        self.buttons['mode'] = tk.Button(self.frames['buttons3'], text="Initial", command=self.toggleMode)
        self.buttons['mode'].pack(side=tk.TOP, fill=tk.X)

        #self.entryip = self.makeform(self.frames['buttons3'], ('Camera IP',)).get('Camera IP')
        #self.entryip.bind('<Enter>', lambda e=None: self.connect())
        self.buttons['ipEnt'], self.buttons['ipBut'] = self.entrybutton(self.frames['buttons3'], 'Camera IP', 'Go', self.toggleConnection)
        self.info['camera'] = tk.Label(self.frames['buttons3'], text="Initial")
        self.info['camera'].pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE)

        #self.frames['screen'] = tk.Frame(self.frames['right'])

        #self.frames['screen'] = Screen(tk.Tk())
        #self.frames['screen'].pack(side=tk.TOP, expand = tk.YES, fill = tk.BOTH)

        self.connected = False
        self.mode = 1
        self.toggleMode()


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


    def addentry(self, master, field, width_label=12, width_entry=None, padx=10, pady=5, multiple=False):

        row = tk.Frame(master)
        lab = tk.Label(row, width=width_label, text=field+': ', anchor='w')
        ent = tk.Entry(row, width=width_entry)
        row.pack(side = tk.TOP if not multiple else tk.LEFT, fill = tk.X, padx = padx , pady = pady)
        lab.pack(side = tk.LEFT)
        ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
        self.entries[field] = ent


    def entrybutton(self, master, field_name, button_name, button_command, width_label=12, width_entry=None, width_button=None, padx=10, pady=5, default=None):
        row = tk.Frame(master)
        lab = tk.Label(row, width=width_label, text=field_name+": ", anchor='w')
        ent = tk.Entry(row, width=width_entry)
        if default:
            ent.insert(0, default)
        but = tk.Button(row, text=button_name, width=width_button, command=button_command)
        row.pack(side = tk.TOP, fill = tk.X, padx = padx, pady = pady)
        lab.pack(side = tk.LEFT)
        ent.pack(side = tk.LEFT, expand=tk.YES, fill = tk.X)
        but.pack(side = tk.RIGHT)
        return (ent, but)


    def save(self):
        for key, entry in self.entries.items():
            print('{}: {}'.format(key, entry.get()))


    def restore(self):
        if self.mode == 0:
            self.modeAdd()
        else:
            pass


    def delete(self):
        pass


    def toggleMode(self):
        if self.mode == 0:
            self.modeEdit()
        else:
            self.modeAdd()

    def modeAdd(self):
        self.mode = 0
        self.info['camera'].config(text = 'Enter camera IP and click Go')
        self.buttons['ipEnt'].config(state ='normal')
        self.buttons['ipBut'].config(text = 'Go')
        self.buttons['ipBut'].config(state ='normal')
        self.buttons['mode'].config(text = 'ADD')
        self.connected = False
        for entry in self.entries.values():
            entry.delete(0, tk.END)


    def modeEdit(self):
        self.mode = 1
        self.info['camera'].config(text = 'Edit mode')
        self.buttons['ipEnt'].config(state ='disabled')
        self.buttons['ipBut'].config(text = 'Go')
        self.buttons['ipBut'].config(state ='disabled')
        self.buttons['mode'].config(text = 'EDIT')
        self.screen = None
        self.connected = False

    def toggleConnection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()


    def connect(self):
        self.info['camera'].config(text = 'Connecting...')
        self.ip = self.buttons['ipEnt'].get()
        if test_ip(self.ip):
            self.info['camera'].config(text = 'Camera online')
            self.buttons['ipBut'].config(text = 'ON')
            self.screen = tk.Toplevel()
            self.connected = True
        else:
            self.info['camera'].config(text = 'Invalid IP. Please retry')


    def disconnect(self):
        self.info['camera'].config(text = 'Camera offline')
        self.buttons['ipBut'].config(text = 'OFF')
        self.screen = None
        self.connected = False


    def refresh(self):
        if self.mode == 0 and self.connected:
            self.array = get_pic(ip=self.ip)
            self.load = Image.fromarray(self.array)
            self.render = ImageTk.PhotoImage(self.load)

            image = tk.Label(self.screen, image=self.render)
            image.place(x=0, y=0)

    def isbnGo(self):
        isbn_in = self.entries['isbn'].get()
        isbn = isbn_in.replace('-','').replace(' ','')

        if isbn != isbn_in:
            self.entries['isbn'].delete(0, tk.END)
            self.entries['isbn'].insert(0, isbn)

        data = get_data(isbn)
        print(data)


    def dumpData(self, data):
        pass

    def navFirst(self):
        pass

    def navPrev(self):
        pass

    def navNext(self):
        pass

    def navLast(self):
        pass

    def navInut(self):
        pass


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
        except (KeyboardInterrupt, tk.TclError):
            break
        time.sleep(.02)


        