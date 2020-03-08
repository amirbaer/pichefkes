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

PAGE_SIZE = 20
TIME_BACK_DAYS = 30
LIMIT_PER_TOPIC = 30
NEWSAPI_KEY = '96c080920fcb45d0ac17ad985534aeba'

#################

class RunParams:

    def __init__(self, time_back_days, page_size, limit_per_topic, topic_filter=None):
        self.tbd = time_back_days
        self.ps = page_size
        self.tf = topic_filter
        self.lpt = limit_per_topic

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
            q=query,
            from_param=(datetime.datetime.now() - datetime.timedelta(days=run_params.tbd)).strftime("%Y-%m-%dT%H:%M:%S"),
            language="en",
            page_size=run_params.ps,
        )

        by_pop = self.newsapi.get_everything(**query_params, sort_by="popularity")
        by_rel = self.newsapi.get_everything(**query_params, sort_by="relevancy")

        by_pop_titles = set(x["title"] for x in by_pop["articles"])
        by_rel_titles = set(x["title"] for x in by_rel["articles"])
        final_titles = by_pop_titles.intersection(by_rel_titles)

        final_articles = []
        for newsapi_article in by_pop["articles"] + by_rel["articles"]:
            if newsapi_article["title"] in final_titles:
                final_articles.append(Article(topic, query, newsapi_article))

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
                total_per_query = 0
                for article in self.newsapi_get_articles(topic, query, run_params):
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
        Date: %s
        Time back in days: %s
        Page size: %s
        Topic filter: %s
        <p>
        <table style='width:100%%'>
        <tr>
            <th width='100'>date</th>
            <th>subject</th>
            <th>query</th>
            <th>header</th>
        </tr>
        """ % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), run_params.tbd, run_params.ps, run_params.tf or "<none>")
        for article in sorted(articles, key=lambda a: (a.topic, a.query, a.date), reverse=True):
                html += """
                <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
                """ % (article.date.strftime("%Y-%m-%d"), article.topic, article.query, article.get_html_link(bt=True))

        html += "</table>\n" 
        open(filename, 'w').write(html)


########## MAIN ###########

def main(out_filename, run_params):
    news_getter = NewsGetter()
    articles = news_getter.get_articles(topic_queries, run_params)
    news_getter.save_as_html(out_filename, articles, run_params)
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: %s <output filename> [<time back days>] [<page size>] [<limit per topic>] [<topic_filter>]" % sys.argv[0])
        sys.exit(1)

    tbd = TIME_BACK_DAYS
    if len(sys.argv) > 2:
        tbd = int(sys.argv[2])

    ps = PAGE_SIZE
    if len(sys.argv) > 3:
        ps = int(sys.argv[3])

    lpt = LIMIT_PER_TOPIC
    if len(sys.argv) > 4:
        lpt = sys.argv[4]

    topic_filter = None
    if len(sys.argv) > 5:
        topic_filter = sys.argv[5]

    main(sys.argv[1], RunParams(tbd, ps, lpt, topic_filter))
