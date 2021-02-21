import requests
import json

from book import Book, Library
from fields import fields

class JsonError(Exception):
    pass
class NotFoundError(Exception):
    pass
class RequestError(Exception):
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

    output = None

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


def fetch(isbn):
    global response

    response = requests.request("GET", url.format('isbn/'+isbn))

    if response.status_code == 404:
        raise NotFoundError
    elif response.status_code != 200:
        raise RequestError(status_code)

    try:
        data1 = json.loads(response.text)
    except:
        raise JsonError
    data = {}

    for (key, val) in data1.items():

        #print('\n=====\n{}'.format(key))
        #print(val)

        data[key] = process_value(val, key in fields)
        #print(data[key])

    return data


def ask(book):
    print('='*70)
    print(book)
    if yesno('\tAdd to library?', 'y'):
        return True
    else:
        return False


def manual():
    raise NotImplementedError


def main():

    library = Library()
    inp = None
    while True:

        inp = input('Input ISBN: >')

        if inp in ['', 'q']:
            break

        try:
            data = fetch(inp)
        except JsonError as e:
            print('Unexpected JSON error', e)
        except RequestError as e:
            print('Unexpected exit status', e)
        except NotFoundError:
            print('Book not found')
            if yesno('Manual input?'):
                data = manual()
        
        else:
            book = Book(**fetch(inp))

            if ask(book):
                library.add(book)

    return library

if __name__ == '__main__':

    library = main()
