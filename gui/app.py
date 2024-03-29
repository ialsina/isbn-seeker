import tkinter as tk


import requests
import json
import time

from .context import Book, Library, fields, Timer, get_data_gui, ask_book, fetch, \
    test_ip, ip2barcode, IsbnError

from .fields import DATA_FIELDS, LOC_FIELDS, JSON2FORM, FORM2JSON, SEPARATOR

from PIL import Image, ImageTk


def quit(process):
    process.destroy()



def load():
    from os import pardir
    from os.path import abspath, join, dirname, isfile
    import pickle


    path = abspath(join(dirname(__file__), pardir, 'data', 'library.pickle'))

    if isfile(path):
        loading = msgbox('yesno', 'Load library from file?', 'Load')
        if loading:
            with open(path, 'rb') as f:
                library = pickle.load(f)
        else:
            library = Library()

    else:
        library = Library()

    return library


def msgbox(mode, message, title=None):
    import tkinter.messagebox as mb
    if mode not in ['yesno', 'info', 'warn', 'err']:
        raise NotImplementedError

    kwargs = dict(title=title, message=message)
    if mode == 'yesno':
        return mb.askyesno(**kwargs)
    elif mode == 'info':
        mb.showinfo(**kwargs)
    elif mode == 'warn':
        mb.showwarning(**kwargs)
    elif mode == 'err':
        mb.showerror(**kwargs)
    return


def filebrowse():
    from tkinter import filedialog
    path = filedialog.asksaveasfilename(initialdir = "~",
        title = "Select a File",
        filetypes = (("Comma separated value","*.csv"),
                     ("Pickle binary file", "*.pickle"),
                     ("all files","*")))
      
    return path



def entrywrite(entry, text):
    entry.delete(0, tk.END)
    entry.insert(0, text)


class App(tk.Frame):
    def __init__(self, master, geometry=None):
        super().__init__(master)

        self.master = master
        self.pack(fill = tk.BOTH, expand = tk.YES)

        if geometry is not None:
            self.master.geometry(geometry)

        self.master.bind('<KeyPress-Home>', self.navFirst)
        self.master.bind('<KeyPress-Prior>', self.navPrev)
        self.master.bind('<KeyPress-Next>', self.navNext)
        self.master.bind('<KeyPress-End>', self.navLast)
        self.master.bind('<Control-KeyPress-Return>', self.store)
        self.master.bind('<Control-KeyPress-Delete>', self.delete)

        self.frames = {}
        self.buttons = {}
        self.labels = {}
        self.entries = {}
        self.entries_loc = {}
        self.info = {}

        self.fields_data = DATA_FIELDS
        self.fields_location = LOC_FIELDS

        self.frames['left'] = tk.Frame(self)
        self.frames['left'].pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        self.frames['right'] = tk.Frame(self)
        self.frames['right'].pack(side = tk.RIGHT, expand = tk.NO, fill = tk.BOTH)

        self.frames['buttons13'] = tk.Frame(self.frames['right'])
        self.frames['buttons13'].pack(side = tk.BOTTOM, expand = tk.YES, fill = tk.X)
        self.frames['buttons12'] = tk.Frame(self.frames['right'])
        self.frames['buttons12'].pack(side = tk.BOTTOM, expand = tk.YES, fill = tk.X)
        self.frames['buttons11'] = tk.Frame(self.frames['right'])
        self.frames['buttons11'].pack(side = tk.BOTTOM, expand = tk.YES, fill = tk.X)

        self.buttons['prev'] = tk.Button(self.frames['buttons11'], text="◀", command=self.navPrev)
        self.buttons['next'] = tk.Button(self.frames['buttons11'], text="▶", command=self.navNext)
        self.buttons['first'] = tk.Button(self.frames['buttons11'], text="◀◀", command=self.navFirst)
        self.buttons['last'] = tk.Button(self.frames['buttons11'], text="▶▶", command=self.navLast)
        self.buttons['idBut'] = tk.Button(self.frames['buttons12'], text='Navigate', command=self.navGoto)

        self.buttons['first'].pack(side=tk.LEFT, expand = tk.YES, fill = tk.X)
        self.buttons['prev'].pack(side=tk.LEFT, expand = tk.YES, fill = tk.X)
        self.buttons['next'].pack(side=tk.LEFT, expand = tk.YES, fill = tk.X)
        self.buttons['last'].pack(side=tk.LEFT, expand = tk.YES, fill = tk.X)
        self.labels['form'] = tk.Label(self.frames['buttons12'], text="Form: ")
        self.buttons['idEnt'] = tk.Entry(self.frames['buttons12'])
        self.buttons['idLab'] = tk.Label(self.frames['buttons12'], text="/Size")
        self.buttons['move'] = tk.Button(self.frames['buttons12'], text='Move', command=self.move)
        self.labels['form'].pack(side=tk.LEFT)
        self.buttons['idEnt'].pack(side=tk.LEFT)
        self.buttons['idLab'].pack(side=tk.LEFT)
        self.buttons['idBut'].pack(side=tk.LEFT)
        self.buttons['move'].pack(side=tk.LEFT)
        self.buttons['export'] = tk.Button(self.frames['buttons13'], text="EXPORT", command=self.export)
        self.buttons['export'].pack(side=tk.TOP, fill = tk.X, expand = tk.YES)
        self.buttons['save'] = tk.Button(self.frames['buttons13'], text="SAVE", command=self.save)
        self.buttons['save'].pack(side=tk.LEFT, fill = tk.X, expand = tk.YES)
        self.buttons['exit'] = tk.Button(self.frames['buttons13'], text="EXIT", command=self.savequit)
        self.buttons['exit'].pack(side=tk.RIGHT, fill = tk.X, expand = tk.YES)

        self.frames['fields'] = tk.Frame(self.frames['left'])
        self.frames['fields'].pack(side = tk.TOP, expand = tk.YES, fill = tk.BOTH)

        loc_row = tk.Frame(self.frames['fields'])
        loc_row.pack(side=tk.TOP, expand = tk.YES, fill =tk.X)
        for field in self.fields_location:
            self.addentry(loc_row, self.entries_loc, field, width_label=8, width_entry=5, multiple=True)

        self.entries['ISBN'], self.buttons['isbnBut'] = self.entrybutton(self.frames['fields'], 'ISBN', 'Search', self.isbnGo)
        for field in self.fields_data[1:]:
            self.addentry(self.frames['fields'], self.entries, field)

        self.frames['buttons2'] = tk.Frame(self.frames['left'])
        self.frames['buttons2'].pack(side=tk.BOTTOM, expand = tk.YES, fill =tk.X)

        self.buttons['store'] = tk.Button(self.frames['buttons2'], text="Add", command=self.store)
        self.buttons['store'].pack(side=tk.LEFT, fill = tk.X, padx=5, expand = tk.YES)
        self.buttons['restore'] = tk.Button(self.frames['buttons2'], text="Restore", command=self.restore)
        self.buttons['restore'].pack(side=tk.LEFT, fill = tk.X, padx=5, expand = tk.YES)
        self.buttons['delete'] = tk.Button(self.frames['buttons2'], text="Delete", command=self.delete)
        self.buttons['delete'].pack(side=tk.LEFT, fill = tk.X, padx=5, expand = tk.YES)


        self.frames['buttons3'] = tk.Frame(self.frames['right'])
        self.frames['buttons3'].pack(side=tk.TOP, expand = tk.YES, fill = tk.X)


        self.buttons['mode'] = tk.Button(self.frames['buttons3'], text="Initial", command=self.toggleMode)
        self.buttons['mode'].pack(side=tk.TOP, fill = tk.X)

        self.buttons['ipEnt'], self.buttons['ipBut'] = self.entrybutton(self.frames['buttons3'], 'Camera IP', 'Go', self.toggleConnection)
        self.info['camera'] = tk.Label(self.frames['buttons3'], text="Initial", justify=tk.LEFT)
        self.info['camera'].pack(side=tk.TOP, expand = tk.YES, fill = tk.X)
        self.info['data'] = tk.Label(self.frames['buttons3'], text="Library offline.")
        self.info['data'].pack(side=tk.TOP, expand = tk.YES, fill = tk.X)


        self.iterator = None
        self.tempdata = None
        self.tempval = None
        self.ip = None
        self.moving = False
        self.unchanged = True

        self.library = load()
        self._update_library()

        self.connected = 0
        self.mode = None
        if len(self.library) == 0:
            self.modeAdd()
        else:
            self.modeEdit(4)


    def _update_library(self, cur=None):
        self.iterator = iter(self.library)
        if cur is not None:
            assert 1 <= cur <= len(self.library)
            self.iterator.set(cur-1)


    def addentry(self, master, entries, field, width_label=12, width_entry=None, padx=10, pady=5, multiple=False):

        row = tk.Frame(master)
        lab = tk.Label(row, width=width_label, text=field+': ', anchor='w')
        ent = tk.Entry(row, width=width_entry)
        row.pack(side = tk.TOP if not multiple else tk.LEFT, expand = tk.YES, fill = tk.BOTH, padx = padx , pady = pady)
        lab.pack(side = tk.LEFT)
        ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.BOTH)
        entries[field] = ent


    def entrybutton(self, master, field_name, button_name, button_command, width_label=12, width_entry=None, width_button=None, padx=10, pady=5, default=None):
        row = tk.Frame(master)
        lab = tk.Label(row, width=width_label, text=field_name+": ", anchor='w')
        ent = tk.Entry(row, width=width_entry)
        if default:
            ent.insert(0, default)
        but = tk.Button(row, text=button_name, width=width_button, command=button_command)
        row.pack(side = tk.TOP, expand = tk.YES, fill = tk.BOTH, padx = padx, pady = pady)
        lab.pack(side = tk.LEFT)
        ent.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        but.pack(side = tk.RIGHT)
        return (ent, but)


    def _update_position(self):

        entrywrite(self.buttons['idEnt'], self.iterator.get()+1)
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
            msgbox('err', 'Separator "{}" can be used only once in the field "Title"'.format(SEPARATOR))

        self.tempdata[FORM2JSON['Title'][0]] = title
        if sub is not None:
            self.tempdata[FORM2JSON['Title'][1]] = sub

        isbn = self.entries['ISBN'].get()
        isbn_type = len(isbn)
        if isbn_type == 10:
            self.tempdata[FORM2JSON['ISBN'][0]] = isbn
        elif isbn_type == 13:
            self.tempdata[FORM2JSON['ISBN'][1]] = isbn
        elif isbn_type == 0:
            self.tempdata[FORM2JSON['ISBN'][0]] = ''
            self.tempdata[FORM2JSON['ISBN'][1]] = ''
        else:
            msgbox('err', 'ISBN must contain 10 or 13 digits', 'ISBN')
            raise IsbnError
            

        for key, val in self.entries.items():
            if key in ['Title', 'ISBN']:
                continue
            value = val.get()
            if ',' in value:
                value = [el.strip() for el in value.split(',')]
            self.tempdata[FORM2JSON.get(key, key)] = value

        for key, val in self.entries_loc.items():
            self.tempdata[FORM2JSON.get(key, key)] = val.get()


    def store(self, event=None):

        self.unchanged = False
        self.tempdata = None

        if self.connected == 2:
            self.connected = 1

        if self.mode == 0:
            self._prepare_data()
            self.library.data_add(self.tempdata)
            self.modeAdd()

        else:
            self.tempdata = self.iterator.cur().data
            self._prepare_data()
            self.library.data_edit(self.iterator.get(), self.tempdata)

        self.tempdata = None
        self._update_position()
        self._update_library(self.iterator.get()+1)


    def restore(self):
        self.dumpData(self.tempdata)


    def delete(self, event=None):

        if self.connected == 2:
            self.connected = 1
        
        if self.mode == 0:
            self.modeAdd()
        else:
            del_id = self.iterator.get() + 1
            if del_id == len(self.library):
                new_id = del_id - 1
            else:
                new_id = del_id

            self.library.delete(del_id - 1)
            entrywrite(self.buttons['idEnt'], new_id)
            self.navigate(5)
            self.modeEdit(0)


    def move(self):
        import time
        if self.mode != 1:
            return

        if not self.moving:
            self.moving = True
            self.buttons['mode'].config(state = 'disabled')
            self.buttons['move'].config(text = 'Drop')
            self.info['data'].config(text='Navigate to desired position and press Drop')
            self.tempval = self.iterator.get() + 1

        elif self.moving:
            self.moving = False
            self.buttons['mode'].config(state = 'normal')
            self.buttons['move'].config(text = 'Move')
            self.library.move(self.tempval-1, self.iterator.get())
            self._update_library()
            self.navigate(5)
            self.tempval = None
            self.modeEdit(0)



    def toggleMode(self):
        if self.mode == 0:
            self.modeEdit(4)
        else:
            self.modeAdd()


    def modeAdd(self):
        self.mode = 0
        self.buttons['ipEnt'].config(state ='normal')
        self.buttons['ipBut'].config(state ='normal')
        self.buttons['mode'].config(text = 'ADD')
        self.buttons['store'].config(text = 'Add')
        self.navigate(4)
        entrywrite(self.buttons['idEnt'], '- NEW -')
        self.buttons['idEnt'].config(state='readonly')
        self.buttons['idLab'].config(text='/'+str(len(self.library)))

        for but in ['first', 'prev', 'next', 'idBut', 'move']:
            self.buttons[but].config(state='disabled')

        for entry in self.entries.values():
            entry.delete(0, tk.END)

        if len(self.library) > 0:
            lastdata = self.iterator.last().data
            for key, entry in self.entries_loc.items():
                entrywrite(entry, lastdata.get(FORM2JSON[key], ''))
        
        if self.connected == 1:
            self.info['data'].config(text='Scanning barcode.')
        else:
            self.info['data'].config(text='Introduce ISBN and click Search.')

        if self.connected == 0:
            self.info['camera'].config(text = 'Enter camera IP and click Go.')
        else:
            self.info['camera'].config(text='Camera online.')

        if len(self.library) == 0:
            self.buttons['mode'].config(state='disabled')
        else:
            self.buttons['mode'].config(state='normal')


    def modeEdit(self, navigate=0):
        if len(self.library) == 0:
            self.modeAdd()
            return

        self.mode = 1
        self.info['camera'].config(text = 'Edit mode. Camera disabled.')
        self.info['data'].config(text = 'Navigate library, edit fields and press Store.')
        self.buttons['ipEnt'].config(state ='disabled')
        self.buttons['ipBut'].config(text = 'Go')
        self.buttons['ipBut'].config(state ='disabled')
        self.buttons['mode'].config(text = 'EDIT')
        self.buttons['store'].config(text = 'Store')
        if navigate in [1, 2, 3, 4]:
            self.navigate(navigate)
        self.buttons['idEnt'].config(state='normal')

        for but in ['first', 'prev', 'next', 'idBut', 'move']:
            self.buttons[but].config(state='normal')

        self.connected = 0
        self._update_position()

    def toggleConnection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()


    def connect(self):
        self.info['camera'].config(text = 'Connecting...')
        ip = self.buttons['ipEnt'].get()
        if test_ip(ip):
            self.info['camera'].config(text = 'Camera online.')
            self.info['data'].config(text = 'Scanning barcode.')
            self.buttons['ipBut'].config(text = 'ON')
            self.connected = 1
            self.ip = ip
        else:
            self.info['camera'].config(text = 'Invalid IP. Please retry.')
            self.ip = None


    def disconnect(self):
        self.info['camera'].config(text = 'Camera offline.')
        self.info['data'].config(text = 'Introduce ISBN and click Search.')
        self.buttons['ipBut'].config(text = 'OFF')
        self.connected = 0



    def isbnGo(self):

        self.info['data'].config(text='Searching book data...')

        isbn_in = self.entries['ISBN'].get()
        isbn = isbn_in.replace('-','').replace(' ','')

        if len(isbn) not in [10, 13]:
            msgbox('err', 'ISBN must contain 10 or 13 digits', 'ISBN')
            self.info['data'].config(text='Invalid ISBN. Please retry.')
            raise IsbnError

        if isbn != isbn_in:
            entrywrite(self.entries['ISBN'], isbn)

        try:
            self.tempdata, exit = get_data_gui(isbn)
        except TypeError:
            print("Unexpeced error")

        if self.tempdata:
            self.info['data'].config(text='Book found. Click Add to confirm.')
            self.dumpData(self.tempdata)
        else:
            self.info['data'].config(text='Book not found. Enter details manually.')
            if self.connected == 2:
                self.connected = 1
            print(exit)


    def dumpData(self, data):
        for key, val in data.items():
            if key in JSON2FORM:
                entry = JSON2FORM[key]
                if entry in self.entries:
                    if isinstance(val, list):
                        val = ', '.join(val)
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

        if isinstance(isbn, list):
            isbn = isbn[0]

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

        if self.tempdata is not None:
            self.dumpData(self.tempdata)

        self._update_position()

    def navGoto(self):
        self.navigate(5)

    def navFirst(self, event=None):
        if self.mode == 1:
            self.navigate(1)

    def navPrev(self, event=None):
        if self.mode == 1:
            self.navigate(2)

    def navNext(self, event=None):
        if self.mode == 1:
            self.navigate(3)

    def navLast(self, event=None):
        if self.mode == 1:
            self.navigate(4)
        if self.mode == 0 and event is None:
            self.copylast()

    def copylast(self):
        if self.mode == 1:
            return

        else:
            self.tempdata = self.iterator.last().data
            self.dumpData(self.tempdata)

    def export(self):
        path = filebrowse()
        try:
            extension = path.split('.')[-1]
        except AttributeError:
            return
        if extension == 'csv':
            print('Exporting csv')
            self.library.export_csv(path = path)
        elif extension == 'pickle':
            print('Exporting pickle')
            self.library.export_obj(path = path)
        else:
            msgbox('err', 'Export supports extensions: .csv, .pickle', 'Export')

    def save(self):
        self.library.save()
        self.unchanged = True

    def savequit(self):
        if not self.unchanged:
            if msgbox('yesno', 'Save library to file?', 'yesno'):
                self.library.save()
        quit(self.master)


    def capture(self):
        try:
            if self.connected == 1:
                barcode = ip2barcode(self.ip)

                if barcode is None:
                    self.info['camera'].configure(text='Camera stream stopped')
                    self.disconnect()
                    return

                if len(barcode) == 1:
                    print('\a', end='\r')
                    entrywrite(self.entries['ISBN'], barcode)
                    self.info['data'].config(text='ISBN found. Searching book data...')
                    self.connected = 2
                    self.update()
                    self.isbnGo()
        except IsbnError:
            print('ISBN error')


if __name__ == '__main__':

    root = tk.Tk()
    myapp = App(root)

    while True:

        try:
            myapp.update()
        except (KeyboardInterrupt, tk.TclError):
            break
        time.sleep(.02)
