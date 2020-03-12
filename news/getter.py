#!/usr/local/bin/python3

import bs4
from bs4 import BeautifulSoup as soup
import datetime
from newsapi import NewsApiClient
import urllib.parse as urlparse
from urllib.parse import urlencode
from urllib.request import urlopen
import sys

from queries import topic_queries
from news_item import Article

#### PARAMS #####

PAGE_SIZE = 30
TIME_BACK_DAYS = 4
LIMIT_PER_TOPIC = 30
QINTITLE = True
NEWSAPI_KEY = '96c080920fcb45d0ac17ad985534aeba'
NEWSAPI_KEY = '5193aa90a389489ab7e77f6edb657e5f'

#################

class RunParams:

    def __init__(self, time_back_days, page_size, limit_per_topic, topic_filter=None,
            qintitle=QINTITLE):
        self.tbd = time_back_days
        self.ps = page_size
        self.tf = topic_filter
        self.lpt = limit_per_topic
        self.qintitle = qintitle

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return "RunParams: %s" % self.__str__()


class NewsGetter:

    def __init__(self):
        self.newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

    def newsapi_get_articles(self, topic, query, run_params):
        " Query NewsAPI and return the intersection between the sorted-by-popularity and the sorted-by-relevancy results"
        query_params = dict(
            qintitle=query,
            from_param=(datetime.datetime.now() - datetime.timedelta(days=run_params.tbd)).strftime("%Y-%m-%dT%H:%M:%S"),
            language="en",
            page_size=run_params.ps,
            sort_by="relevancy",
        )

        if run_params.qintitle:
            query_params["qintitle"] = query
        else:
            query_params["q"] = query

        newsapi_articles = self.newsapi.get_everything(**query_params)["articles"]
        final_articles = [Article(topic, query, article) for article in newsapi_articles]
        return final_articles

    def get_articles(self, topic_queries, run_params):
        articles = []
        titles_seen = set()

        print("RUN PARAMS: days back: %(tbd)s, page size: %(ps)s, limit per topic: %(lpt)s, topic filter: %(tf)s" % run_params.__dict__)

        for topic, queries in topic_queries.items():
            if run_params.tf and topic != run_params.tf.lower():
                continue
            print("Topic: %s" % topic)
            topic_articles = []
            for query in queries:
                print("'%s': " % query, end="")
                total_per_query = 0
                newsapi_articles = self.newsapi_get_articles(topic, query, run_params)
                print("%s" % len(newsapi_articles))
                for article in newsapi_articles:
                    title = article.title
                    if title in titles_seen:
                        print("-> skipping: %s" % title)
                        continue

                    topic_articles.append(article)
                    titles_seen.add(title)
                    total_per_query += 1

            topic_articles = sorted(topic_articles, key=lambda a: a.date, reverse=True)
            if run_params.lpt and len(topic_articles) >= run_params.lpt:
                print("-> [XXX] topic limit (%s) surpassed (%s)" % (run_params.lpt,
								    len(topic_articles)))
                topic_articles = topic_articles[:run_params.lpt]
            articles += topic_articles

        return articles

    def save_as_html(self, filename, articles, run_params):
        html = """
        <html>
        <head><style>
        td.date {
            white-space: nowrap;
            color: green;
        }
        td.query {
            white-space: nowrap;
            color: red;
        }
        td.source {
            font-size: 10;
            font-weight: bold;
            color: orange;
        }
        td.header {
            white-space: nowrap;
        }
        td.content {
            white-space: nowrap;
        }
        </style></head>
        Date: %s
        Time back in days: %s
        Page size: %s
        Topic filter: %s
        Query title only: %s
        <p>
        <table style='width:100%%'>
        <tr>
            <th>date</th>
            <th>subject</th>
            <th>query</th>
            <th>source</th>
            <th>header</th>
            <th>content</th>
        </tr>
        """ % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), run_params.tbd,
                run_params.ps, run_params.tf or "<none>", run_params.qintitle)
        for article in sorted(articles, key=lambda a: (a.topic, a.query, a.date), reverse=True):
                html += """
                <tr>
                    <td class="date">%s</td>
                    <td class="topic">%s</td>
                    <td class="query">%s</td>
                    <td class="source">%s</td>
                    <td class="header">%s</td>
                    <td class="content">%s</td>
                </tr>
                """ % (article.date.strftime("%Y-%m-%d"), article.topic, article.query,
                        article.source, article.get_html_link(bt=True), article.content)

        html += "</table>\n</html>" 
        open(filename, 'w').write(html)


########## MAIN ###########

def main(out_filename, run_params):
    news_getter = NewsGetter()
    articles = news_getter.get_articles(topic_queries, run_params)
    news_getter.save_as_html(out_filename, articles, run_params)
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: %s <output filename> [<topic_filter>] [<time back days>] [<page size>] [<limit per topic>]" % sys.argv[0])
        sys.exit(1)

    topic_filter = None
    if len(sys.argv) > 2:
        topic_filter = sys.argv[2]

    tbd = TIME_BACK_DAYS
    if len(sys.argv) > 3:
        tbd = int(sys.argv[3])

    ps = PAGE_SIZE
    if len(sys.argv) > 4:
        ps = int(sys.argv[4])

    lpt = LIMIT_PER_TOPIC
    if len(sys.argv) > 5:
        lpt = int(sys.argv[5])

    main(sys.argv[1], RunParams(tbd, ps, lpt, topic_filter))
