import tkinter as tk

from include import Book, Library, fields, Timer, get_data, ask_book, fetch, \
    get_barcode, get_pic, ask_url

from gui import App, Screen

if __name__ == '__main__':

    root = tk.Tk()
    myapp = App(root)

    myapp.mainloop()
