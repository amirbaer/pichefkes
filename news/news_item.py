
class Item:
    def __init__(self, title, link, date, original_query, dewey=[]):
        self.title = title
        self.link = link
        self.date = date
        self.original_query = original_query
        self.dewey = dewey

