from os import pardir
from os.path import join, abspath, dirname
import csv
import pickle

class Library:
    def __init__(self):
        self.count = 0

        self.library = []

    def __len__(self):
        return len(self.library)

    def __getitem__(self, item):
        self._checkitem(item)
        return self.library[item]

    def __setitem__(self, item, element):
        self._checkitem(item)
        self.library[item] = element


    def __delitem__(self, item):
        self._checkitem(item)
        del self.library[item]


    def __iter__(self):
        return LibraryIterator(self)

    def _checkitem(self, item):
        assert isinstance(item, int)
        assert 0 <= item < len(self.library)

    def data_add(self, data):
        self.add(Book(**data))

    def data_edit(self, index, data):
        self[index] = Book(**data)

    def add(self, book):
        assert isinstance(book, Book)
        self.count += 1
        self.library.append(book)


    def move(self, origin, destination):
        self._checkitem(origin)
        self._checkitem(destination)

        element = self.library.pop(origin)
        self.library = self.library[:destination] + [element] + self.library[destination:]

    def delete(self, item):
        del self[item]


    def search(self, query):
        found = []

        for book in self.library:
            if book.matches(query):
                found.append(book)

        if len(found) == 0:
            return

        elif len(found) == 1:
            return found[0]

        else:
            return found

    def export_csv(self):
        from ordered_set import OrderedSet

        fields = OrderedSet(['room', 'module', 'shelf', 'title', 'authors', 'publishers',
            'subjects', 'isbn_13', 'isbn_10', 'publish_date', 'revision'])

        for book in self.library:
            for field in book.data.keys():
                fields.add(field)

        path = abspath(join(dirname(__file__), pardir, 'data', 'library.csv'))
        with open(path, 'w') as f:
            writer = csv.writer(f, delimiter=';', quotechar='"')
            writer.writerow(['#'] + list(fields))
            for i, book in enumerate(self.library):
                row = [book.get(field,'') for field in fields]
                writer.writerow([i+1] + row)



    def export_obj(self):
        path = abspath(join(dirname(__file__), pardir, 'data', 'library.pickle'))
        with open(path, 'wb') as f:
            pickle.dump(self, f)


    def save(self):
        self.export_csv()
        self.export_obj()



class LibraryIterator:
    def __init__(self, library):
        self._index = 0
        self._library = library
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._index < len(self._library):
            x = self._index
            self._index += 1
            return self._library[x] 
        else:
            raise StopIteration

    def get(self):
        return self._index

    def set(self, ind):
        self._library._checkitem(ind)
        self._index = ind

    def ret(self):
        return self._library[self._index]

    def first(self):
        self._index = 0
        return self.ret()

    def last(self):
        self._index = len(self._library) - 1
        return self.ret()

    def prev(self):
        if self._index > 0:
            self._index -= 1
            return self.ret()
        else:
            raise IndexError

    def next(self):
        if self._index < len(self._library) - 1:
            self._index += 1
            return self.ret()
        else:
            raise IndexError

    cur = ret

    def goto(self, ind):
        ind = int(ind)
        if ind >= 0 and ind <= len(self._library) - 1:
            self._index = ind
            return self.ret()
        else:
            raise IndexError



class Book:
    def __init__(self, **data):
        self.data = {}

        for (key, val) in data.items():
            self.data[key] = val

        if self.get('weight'):
            pass

    def __repr__(self):
        return '\t{} {}\n\t{}\n\t{}\n\t'.format(
                    self.get('title'), 
                    self.get('subtitle'), 
                    self.get('authors'), 
                    self.get('publishers')
                    )

    def print(self):
        for key, val in self.data.items():
            try:
                print('{:>30s}: {:<45}'.format(key, val))
            except:
                continue

    def get(self, query, otherwise=''):
        output = self.data.get(query)
        if output is None:
            return otherwise

        if isinstance(output, list):
            return ', '.join(output)

        elif isinstance(output, dict):
            return ', '.join(['{}: {}'.format(k, v) for k, v in output.items()])

        else:
            return str(output)

    def is_author(self, query):
        pass

    def is_title(self, query):
        pass

    def is_publisher(self, query):
        pass