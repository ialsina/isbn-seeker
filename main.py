import requests
import json
import time

from book import Book, Library
from fields import fields
from timer import Timer

from isbn import get_data, ask_book
from barscan import get_barcode, get_pic, get_url



def main(library=None):

    if library is None:
        library = Library()

    url = get_url()

    inp = None
    while True:

        barcode = get_barcode(get_pic(url))

        if len(barcode) == 1:
            print('Barcode found:', barcode[0])
            data = get_data(barcode[0])
        else:
            continue

        if len(data) == 0:
            continue

        book = Book(**data)

        if ask_book(book):
            library.add(book)

        time.sleep(0.5)

    return library

if __name__ == '__main__':

    library = main()
