from datetime import datetime

class Item:
    def __init__(self, title, link, date, original_query, dewey=[]):
        self.title = title
        self.link = link
        self.date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z") 
        self.original_query = original_query
        self.dewey = dewey

