from datetime import datetime
import re


class Article:
    def __init__(self, topic, query, newsapi_article):
        self.topic = topic
        self.query = query

        self.title = newsapi_article["title"]
        self.link = newsapi_article["url"]
        self.date = datetime.strptime(newsapi_article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ") 
        self.description = newsapi_article["description"]


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

