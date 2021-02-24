
DATA_FIELDS = ['ISBN', 'Title', 'Author', 'Publisher', 'Subjects', 'Publish date', 'Revision']
LOC_FIELDS = ['Room', 'Module', 'Shelf']


JSON2FORM = {
    'title' : 'Title',
    'subtitle' : 'Title',
    'authors' : 'Author',
    'publishers' : 'Publisher',
    'subjects' : 'Subjects',
    'publish_date': 'Publish date',
    'revision' : 'Revision',
    'room' : 'Room',
    'module' : 'Module',
    'shelf' : 'Shelf',
}

FORM2JSON = {v: k for k, v in JSON2FORM.items()}
FORM2JSON['Title'] = ['title', 'subtitle']
FORM2JSON['ISBN'] = ['isbn_10', 'isbn_13']
SEPARATOR = '//'