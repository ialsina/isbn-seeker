import tkinter as tk


import requests
import json
import time

from .context import Book, Library, fields, Timer, get_data_gui, ask_book, fetch, \
    get_barcode, get_pic, ask_url

from .fields import DATA_FIELDS, LOC_FIELDS, JSON2FORM, FORM2JSON, SEPARATOR

from PIL import Image, ImageTk


def quit(process):
    process.destroy()



def load():
    from os import pardir
    from os.path import abspath, join, dirname, isfile
    import pickle
    import tkinter.messagebox as mb


    path = abspath(join(dirname(__file__), pardir, 'data', 'library.pickle'))

    if isfile(path):
        loading = mb.askyesno(title='Library', message='Load library from file?')
        if loading:
            with open(path, 'rb') as f:
                library = pickle.load(f)
        else:
            library = Library()

    else:
        library = Library()

    return library


def entrywrite(entry, text):
    entry.delete(0, tk.END)
    entry.insert(0, text)


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.pack()

        self.frames = {}
        self.buttons = {}
        self.labels = {}
        self.entries = {}
        self.entries_loc = {}
        self.info = {}

        self.fields_data = DATA_FIELDS
        self.fields_location = LOC_FIELDS

        self.frames['left'] = tk.Frame(self.master)
        self.frames['left'].pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        self.frames['right'] = tk.Frame(self.master)
        self.frames['right'].pack(side = tk.RIGHT, expand = tk.YES, fill = tk.BOTH)

        self.frames['buttons12'] = tk.Frame(self.frames['right'])
        self.frames['buttons12'].pack(side = tk.BOTTOM, expand = tk.YES, fill = tk.X)
        self.frames['buttons11'] = tk.Frame(self.frames['right'])
        self.frames['buttons11'].pack(side = tk.BOTTOM, expand = tk.YES, fill = tk.X)

        self.buttons['prev'] = tk.Button(self.frames['buttons11'], text="◀", command=lambda: self.navigate(2))
        self.buttons['next'] = tk.Button(self.frames['buttons11'], text="▶", command=lambda: self.navigate(3))
        self.buttons['first'] = tk.Button(self.frames['buttons11'], text="◀◀", command=lambda: self.navigate(1))
        self.buttons['last'] = tk.Button(self.frames['buttons11'], text="▶▶", command=lambda: self.navigate(4))
        self.buttons['idBut'] = tk.Button(self.frames['buttons12'], text='Navigate', command=lambda: self.navigate(5))

        self.buttons['first'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.buttons['prev'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.buttons['next'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.buttons['last'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.labels['form'] = tk.Label(self.frames['buttons12'], text="Form: ")
        self.buttons['idEnt'] = tk.Entry(self.frames['buttons12'])
        self.buttons['idLab'] = tk.Label(self.frames['buttons12'], text="/Size")
        self.labels['form'].pack(side=tk.LEFT)
        self.buttons['idEnt'].pack(side=tk.LEFT)
        self.buttons['idLab'].pack(side=tk.LEFT)
        self.buttons['idBut'].pack(side=tk.LEFT)
        self.buttons['exit'] = tk.Button(self.frames['buttons12'], text="EXIT", command=self.savequit)
        self.buttons['exit'].pack(side=tk.LEFT)

        self.frames['fields'] = tk.Frame(self.frames['left'])
        self.frames['fields'].pack(side = tk.TOP, expand = tk.YES, fill = tk.BOTH)

        loc_row = tk.Frame(self.frames['fields'])
        loc_row.pack(side=tk.TOP, expand=tk.YES, fill =tk.X)
        for field in self.fields_location:
            self.addentry(loc_row, self.entries_loc, field, width_label=8, width_entry=5, multiple=True)

        self.entries['ISBN'], self.buttons['isbnBut'] = self.entrybutton(self.frames['fields'], 'ISBN', 'Search', self.isbnGo)
        for field in self.fields_data[1:]:
            self.addentry(self.frames['fields'], self.entries, field)

        self.frames['buttons2'] = tk.Frame(self.frames['left'])
        self.frames['buttons2'].pack(side=tk.BOTTOM, expand = tk.YES, fill =tk.X)

        self.buttons['save'] = tk.Button(self.frames['buttons2'], text="Save", command=self.save)
        self.buttons['save'].pack(side=tk.LEFT, fill=tk.X, padx=5, expand=tk.YES)
        self.buttons['restore'] = tk.Button(self.frames['buttons2'], text="Restore", command=self.restore)
        self.buttons['restore'].pack(side=tk.LEFT, fill=tk.X, padx=5, expand=tk.YES)
        self.buttons['delete'] = tk.Button(self.frames['buttons2'], text="Delete", command=self.delete)
        self.buttons['delete'].pack(side=tk.LEFT, fill=tk.X, padx=5, expand=tk.YES)


        self.frames['buttons3'] = tk.Frame(self.frames['right'])
        self.frames['buttons3'].pack(side=tk.TOP, expand = tk.YES, fill = tk.X)


        self.buttons['mode'] = tk.Button(self.frames['buttons3'], text="Initial", command=self.toggleMode)
        self.buttons['mode'].pack(side=tk.TOP, fill=tk.X)

        self.buttons['ipEnt'], self.buttons['ipBut'] = self.entrybutton(self.frames['buttons3'], 'Camera IP', 'Go', self.toggleConnection)
        self.info['camera'] = tk.Label(self.frames['buttons3'], text="Initial", justify=tk.LEFT)
        self.info['camera'].pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        self.info['data'] = tk.Label(self.frames['buttons3'], text="Library offline.")
        self.info['data'].pack(side=tk.TOP, expand=tk.YES, fill=tk.X)


        self.iterator = None
        self.tempdata = None
        self.library = load()
        self._update_library()

        self.connected = False
        self.mode = None
        if len(self.library) == 0:
            self.modeAdd()
        else:
            self.modeEdit()


    def _update_library(self):
        self.iterator = iter(self.library)


    def addentry(self, master, entries, field, width_label=12, width_entry=None, padx=10, pady=5, multiple=False):

        row = tk.Frame(master)
        lab = tk.Label(row, width=width_label, text=field+': ', anchor='w')
        ent = tk.Entry(row, width=width_entry)
        row.pack(side = tk.TOP if not multiple else tk.LEFT, fill = tk.X, padx = padx , pady = pady)
        lab.pack(side = tk.LEFT)
        ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
        entries[field] = ent


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


    def _update_position(self):

        entrywrite(self.buttons['idEnt'], self.iterator.index+1)
        self.buttons['idLab'].config(text='/'+str(len(self.library)))


    def _prepare_data(self):
        self.tempdata = self.tempdata or {}

        titsub = self.entries['Title'].get().split(SEPARATOR)
        titsub = [el.strip() for el in titsub]
        if len(titsub) == 1:
            title = titsub[0]
            sub = None
        elif len(titsub) == 2:
            title, sub = titsub
        else:
            raise RuntimeError

        self.tempdata[FORM2JSON['Title'][0]] = title
        if sub is not None:
            self.tempdata[FORM2JSON['Title'][1]] = sub

        isbn_type = len(self.entries['ISBN'].get())
        if isbn_type == 10:
            self.tempdata[FORM2JSON['ISBN'][0]]
        elif isbn_type == 13:
            self.tempdata[FORM2JSON['ISBN'][1]]
        elif isbn_type == 0:
            pass
        else:
            raise RuntimeError('ISBN')
            

        for key, val in self.entries.items():
            if key in ['Title', 'ISBN']:
                continue
            self.tempdata[FORM2JSON.get(key, key)] = val.get()

        for key, val in self.entries_loc.items():
            self.tempdata[FORM2JSON.get(key, key)] = val.get()


    def save(self):

        if self.mode == 0:
            self._prepare_data()
            self.library.data_add(self.tempdata)
            self.modeAdd()

        else:
            self.tempdata = self.iterator.cur().data
            self._prepare_data()
            self.library.data_edit(self.iterator.index, self.tempdata)

        self.tempdata = None
        self._update_position()
        self._update_library()


    def restore(self):
        self.dumpData(self.tempdata)


    def delete(self):
        
        if self.mode == 0:
            self.modeAdd()
        else:
            del_id = self.iterator.index + 1
            if del_id == len(self.library):
                new_id = del_id - 1
            else:
                new_id = del_id

            self.library.delete(del_id - 1)
            entrywrite(self.buttons['idEnt'], new_id)
            self.navigate(5)
            self.modeEdit()



    def toggleMode(self):
        if self.mode == 0:
            self.modeEdit()
        else:
            self.modeAdd()


    def modeAdd(self):
        self.mode = 0
        self.info['camera'].config(text = 'Enter camera IP and click Go.')
        self.buttons['ipEnt'].config(state ='normal')
        self.buttons['ipBut'].config(text = 'Go')
        self.buttons['ipBut'].config(state ='normal')
        self.buttons['mode'].config(text = 'ADD')
        self.navigate(4)
        entrywrite(self.buttons['idEnt'], '- NEW -')
        self.buttons['idEnt'].config(state='readonly')
        self.buttons['idLab'].config(text='/'+str(len(self.library)))

        for but in ['first', 'last', 'prev', 'next', 'idBut']:
            self.buttons[but].config(state='disabled')

        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        if self.connected:
            self.info['data'].config(text='Scanning barcode.')
        else:
            self.info['data'].config(text='Introduce IBAN and click Search.')

        if len(self.library) == 0:
            self.buttons['mode'].config(state='disabled')
        else:
            self.buttons['mode'].config(state='normal')


    def modeEdit(self):
        if len(self.library) == 0:
            self.modeAdd()
            return

        self.mode = 1
        self.info['camera'].config(text = 'Edit mode. Camera disabled.')
        self.buttons['ipEnt'].config(state ='disabled')
        self.buttons['ipBut'].config(text = 'Go')
        self.buttons['ipBut'].config(state ='disabled')
        self.buttons['mode'].config(text = 'EDIT')
        self.navigate(1)
        self.buttons['idBut'].config(state='normal')
        self.buttons['idEnt'].config(state='normal')
        self.screen = None

        for but in ['first', 'last', 'prev', 'next', 'idBut']:
            self.buttons[but].config(state='normal')

        self.connected = False
        self._update_position()

    def toggleConnection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()


    def connect(self):
        self.info['camera'].config(text = 'Connecting...')
        self.ip = self.buttons['ipEnt'].get()
        if test_ip(self.ip):
            self.info['camera'].config(text = 'Camera online.')
            self.buttons['ipBut'].config(text = 'ON')
            self.screen = tk.Toplevel()
            self.connected = True
        else:
            self.info['camera'].config(text = 'Invalid IP. Please retry.')


    def disconnect(self):
        self.info['camera'].config(text = 'Camera offline.')
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
        self.info['data'].config(text='Searching ISBN...')

        isbn_in = self.entries['ISBN'].get()
        isbn = isbn_in.replace('-','').replace(' ','')

        if isbn != isbn_in:
            entrywrite(self.entries['ISBN'], isbn)

        self.tempdata = get_data_gui(isbn)

        if self.tempdata:
            self.info['data'].config(text='Book found. Click Save to confirm.')
            self.dumpData(self.tempdata)
        else:
            self.info['data'].config(text='Book not found. Enter details manually.')


    def dumpData(self, data):
        for key, val in data.items():
            if key in JSON2FORM:
                entry = JSON2FORM[key]
                if entry in self.entries:
                    entrywrite(self.entries[entry], val)
                elif entry in self.entries_loc:
                    entrywrite(self.entries_loc[entry], val)

        if 'subtitle' in data:
            titsub = data.get('title', '') + ' {} '.format(SEPARATOR) + data['subtitle']
            entrywrite(self.entries['Title'], titsub)

        if data.get('isbn_13'):
            isbn = data.get('isbn_13')
        elif data.get('isbn_10'):
            isbn = data.get('isbn_10')
        else:
            isbn = ''

        entrywrite(self.entries['ISBN'], isbn)

    def navigate(self, where):
        if self.mode == 0:
            return

        if len(self.library) == 0:
            return

        try:
            if where == 1:
                self.tempdata = self.iterator.first().data
            elif where == 2:
                self.tempdata = self.iterator.prev().data
            elif where == 3:
                self.tempdata = self.iterator.next().data
            elif where == 4:
                self.tempdata = self.iterator.last().data
            elif where == 5:
                self.tempdata = self.iterator.goto(int(self.buttons['idEnt'].get())-1).data
        except IndexError:
            pass

        self.dumpData(self.tempdata)

        self._update_position()

    def savequit(self):
        self.library.save()
        quit(self.master)



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


        