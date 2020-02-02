from datetime import datetime
import re

class Item:
    def __init__(self, title, link, date, description, original_query, dewey=[]):
        self.title = title
        self.link = link
        self.date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z") 
        self.description = description
        self.original_query = original_query
        self.dewey = dewey

        if not self.link:
            desc_link_res = re.findall(r'a href="([^"]*)"', self.description)
            if desc_link_res:
                self.link = desc_link_res[0]

