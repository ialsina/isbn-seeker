import tkinter as tk

from include import Book, Library, fields, Timer, get_data, ask_book, fetch, \
    get_barcode, get_pic, ask_url

from gui import App

if __name__ == '__main__':

    root = tk.Tk()
    myapp = App(root)

    while True:
        try:
            myapp.update_idletasks()
            myapp.update()
            myapp.capture()
        except tk.TclError:
            pass
