from datetime import datetime
import re

class Item:
    def __init__(self, title, link, date, description, topic, original_query):
        self.title = title
        self.link = link
        self.date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z") 
        self.description = description

        self.topic = topic
        self.original_query = original_query

        if not self.link:
            desc_link_res = re.findall(r'a href="([^"]*)"', self.description)
            if desc_link_res:
                self.link = desc_link_res[0]

    def get_html_link(self, bt=False):
        title = self.get_bolded_title() if bt else self.title
        return '<a href="%s">%s</a>' % (self.link, title)

    def get_excel_link(self, bt=False):
        title = self.get_bolded_title() if bt else self.title
        return '=HYPERLINK("%s", "%s")' % (self.link, title)

    def get_bolded_title(self):
        parts = []
        for word in self.title.replace("-", " ").split(" "):
            search_word = "".join([c.lower() for c in word if c.isalnum()])
            if search_word in self.original_query.lower():
                word = "<b>%s</b>" % word
            parts.append(word)

        return " ".join(parts)

