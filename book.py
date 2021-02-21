class Library:
    def __init__(self):
        self.count = 0

        self.library = []

    def __getitem__(self, item):
        return self.library[item]


    def add(self, book):
        assert isinstance(book, Book)
        self.count += 1
        self.library.append(book)


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

class Book:
    def __init__(self, **data):
        self.data = {}

        for (key, val) in data.items():
            self.data[key] = val

    def __repr__(self):
        return '\t{}\n\t{}\n\t{}\n\t{}\n\t'.format(
                    self.get('title'), 
                    self.get('subtitle'), 
                    self.get('authors'), 
                    self.get('publishers')
                    )

    def get(self, query):
        return self.data.get(query) or '-'

    def is_author(self, query):
        pass

    def is_title(self, query):
        pass

    def is_publisher(self, query):
        pass