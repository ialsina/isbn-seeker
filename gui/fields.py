
DATA_FIELDS = ['ISBN', 'Title', 'Author', 'Publisher', 'Subjects']
LOC_FIELDS = ['Room', 'Module', 'Shelf']


JSON2FORM = {
    'title' : 'Title',
    'subtitle' : 'Title',
    'authors' : 'Author',
    'publishers' : 'Publisher',
    'subjects' : 'Subjects',
    'room' : 'Room',
    'module' : 'Module',
    'shelf' : 'Shelf',
}

FORM2JSON = {v: k for k, v in JSON2FORM.items()}
FORM2JSON['Title'] = ['title', 'subtitle']
FORM2JSON['ISBN'] = ['isbn_10', 'isbn_13']
SEPARATOR = '//'