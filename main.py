import requests
import json
import time

from include import Book, Library, fields, Timer, get_data, ask_book, fetch, \
    get_barcode, get_pic, ask_url


ex = None
def ask_action():
    inp = None
    print('Input action:\n\tISBN [s]can\n\t[i]SBN manual input\n\t[b]ook details manual input\n\tE[x]it')
    inp = input('\n\t>')
    while inp not in ['s', 'i', 'b', 'x']:
        print('Invalid action')
        inp = input('\n\t>')

    return {'s': 1, 'm': 2, 'b': 3, 'x': 0}.get(inp)


def readcam(url):

    print('Reading', end='\r')

    try:
        while True:

            barcode = get_barcode(get_pic(url))

            if len(barcode) == 1:
                print('Barcode found:', barcode[0])
                return barcode[0]

            time.sleep(0.5)

    except KeyboardInterrupt:
        print('Reading stopped')
        raise KeyboardInterrupt



def main():

    global library

    if library is None:
        library = Library()

    try:
        url = ask_url()
    except KeyboardInterrupt:
        return

    while True:

        action = ask_action()

        if action == 0:
            print('Camera status: offline')
            print('Exit program')
            break

        elif action == 1:
            try:
                isbn = readcam(url)
                data = get_data(isbn)
            except KeyboardInterrupt:
                continue

        elif action == 2:
            try:
                isbn = ask_isbn()
                data = get_data(isbn)
            except KeyboardInterrupt:
                continue

        elif action == 3:
            try:
                data = manual()
            except KeyboardInterrupt:
                continue
            except NotImplementedError:
                print('Not available')
                continue

        if data is None:
            continue

        book = Book(**data)

        if ask_book(book):
            library.add(book)

if __name__ == '__main__':

    library = None
    main()
