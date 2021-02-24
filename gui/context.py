import sys
from os import pardir
from os.path import join, abspath, dirname

sys.path.insert(0, abspath(join(dirname(__file__), pardir)))

from include import Book, Library, fields, Timer, get_data, ask_book, fetch, \
    get_barcode, get_pic, ask_url
