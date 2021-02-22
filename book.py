import csv
import pickle

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

    def export_csv(self):
        fields = set()

        for book in self.library:
            for field in book.data.keys():
                fields.add(field)

        fields = list(fields)
        with open('library.csv', 'w') as f:
            writer = csv.writer(f, delimiter=';', quotechar='"')
            writer.writerow(fields)
            for book in self.library:
                row = [book.get(field,'') for field in fields]
                writer.writerow(row)



    def export_obj(self):
        with open('library.pickle', 'wb') as f:
            pickle.dump(self, f)


    def save(self):
        self.export_csv()
        self.export_obj()


class Book:
    def __init__(self, **data):
        self.data = {}

        for (key, val) in data.items():
            self.data[key] = val

        if self.get('weight'):


    def __repr__(self):
        return '\t{} {}\n\t{}\n\t{}\n\t'.format(
                    self.get('title'), 
                    self.get('subtitle'), 
                    self.get('authors'), 
                    self.get('publishers')
                    )

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