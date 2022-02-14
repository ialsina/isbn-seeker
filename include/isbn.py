import requests
import json

try:
    from .book import Book, Library
    from .fields import fields
    from .timer import Timer
except ImportError:
    from book import Book, Library
    from fields import fields
    from timer import Timer


class JsonError(Exception):
    pass
class NotFoundError(Exception):
    pass
class RequestError(Exception):
    pass
class IsbnError(Exception):
    pass

isbn1 = '9984922901'

response = None

url = "https://openlibrary.org/{}.json"

def yesno(text, default=None):
    yes = ['y', 'yes', 'Y', 'Yes', 'YES', '1']
    no = ['n', 'no', 'N', 'No', 'NO', '0']

    if default == 'y':
        yn = '[(y)/n]'
    elif default == 'n':
        yn = '[y/(n)]'
    else:
        yn = '[y/n]'

    question = '{} {} >'.format(text, yn)

    inp = input(question)

    if default == 'y':
        return inp not in no
    elif default == 'n':
        return inp in yes
    else:
        while True:
            if inp in yes:
                return True
            elif inp in no:
                return False
            else:
                print('Invalid answer')
                inp = input(question)



def refetch(entry):
    source1 = entry.get('key')
    source2 = entry.get('location')

    sources = list(filter(None, [source2, source1]))

    for source in sources:

        new_info = requests.request("GET", url.format(source)).text
        new_info_json = json.loads(new_info)
        if 'name' in new_info_json:
            return new_info_json.get('name')
    
    return refetch(new_info_json)

def process_single(entry, careful=True):

    if isinstance(entry, dict):
        if 'key' in entry and careful:
            return refetch(entry)
                
        else:
            temp = {}
            for (key, val) in entry.items():
                temp[key] = process_value(val, careful)
            return temp

    else:
        return entry

def process_value(value, careful=True):
    if isinstance(value, list):
        temp = []

        for entry in value:
            temp.append(process_single(entry, careful))

        if len(temp) == 1:
            return temp[0]

        else:
            return temp

    else:
        return process_single(value, careful)


def fetch(isbn, tim=Timer(False)):
    global response

    tim.lap()

    response = requests.request("GET", url.format('isbn/'+isbn))


    if response.status_code == 404:
        raise NotFoundError('Book not found: {}'.format(isbn))
    elif response.status_code != 200:
        raise RequestError('Response error', status_code)

    tim.lap()

    try:
        data1 = json.loads(response.text)
    except:
        raise JsonError('Error on JSON load')
    data = {}

    tim.lap()

    for (key, val) in data1.items():

        data[key] = process_value(val, key in fields)

        tim.lap()

    if 'error' in data:
        raise NotFoundError(data.get('error'))

    return data


def ask_book(book):
    print('='*70)
    print(book)
    if yesno('\tAdd to library?', 'y'):
        return True
    else:
        return False


def manual():
    raise NotImplementedError


def get_data(isbn):
    try:
        data = fetch(isbn)
    except JsonError as e:
        print('Unexpected JSON error', e)
        return {}
    except RequestError as e:
        print('Unexpected exit status', e)
        return {}
    except NotFoundError:
        print('Book not found: {}'.format(isbn))
        if yesno('Manual input?'):
            data = manual()
    else:
        return data


def get_data_gui(isbn, tries=3):
    for i in range(1, tries+1):
        try:
            data = fetch(isbn)
            return (data, 0)
        except JsonError as e:
            if i == tries:
                return ({}, e)
        except RequestError as e:
            if i == tries:
                return ({}, e)
        except NotFoundError as e:
            if i == tries:
                return ({}, e)
        except Exception as e:
            if i == tries:
                return ({}, e)


def ask_isbn():
    inp = input('Input ISBN: >')

    if inp in ['', 'q']:
        raise KeyboardInterrupt

    return inp.replace('-','').replace(' ','')




def main(library=None):

    if library is None:
        library = Library()

    while True:

        try:
            isbn = ask_isbn()
        except KeyboardInterrupt:
            break

        data = get_data(isbn)

        if len(data) == 0:
            continue

        book = Book(**data)

        if ask_book(book):
            library.add(book)

    library.save()

    return library

if __name__ == '__main__':

    library = main()
