#!/usr/local/bin/python3

import bs4
from bs4 import BeautifulSoup as soup
import urllib.parse as urlparse
from urllib.parse import urlencode
from urllib.request import urlopen
import sys

from queries import topic_queries
from news_item import Item

#### PARAMS #####

LIMIT_RESULTS_PER_QUERY = 10
LIMIT_RESULTS_PER_TOPIC = 100

#################

def get_query_url(query):
    news_url="https://news.google.com/news/rss"
    params = {'q': query, 'lang':'en'}

    url_parts = list(urlparse.urlparse(news_url))
    query_dict = dict(urlparse.parse_qsl(url_parts[4]))
    query_dict.update(params)

    url_parts[4] = urlencode(query_dict)
    return urlparse.urlunparse(url_parts)

# TODO: paging
def get_news_items(topic, query):
    query_url = get_query_url(query)
    client = urlopen(query_url)
    xml_page = client.read()
    client.close()

    news_items = []
    soup_page = soup(xml_page, "html.parser")
    for news in soup_page.findAll("item"):
        news_items.append(Item(
            news.title.text,
            news.link.text,
            news.pubdate.text,
            news.description.text,
            topic,
            query,
        ))

    return news_items

def save_as_html(filename, articles):
    html = """
    <table style='width:100%'>
    <tr>
        <th width='100'>date</th>
        <th>subject</th>
        <th>query</th>
        <th>header</th>
    </tr>
    """
    for item in sorted(articles, key=lambda a: (a.topic, a.original_query, a.date), reverse=True):
            html += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """ % (item.date.strftime("%Y-%m-%d"), item.topic, item.original_query, item.get_html_link(bt=True))

    html += "</table>\n" 
    open(filename, 'w').write(html)

def update(tqs, lpt=None, lpq=None):
    articles = []
    titles_seen = set()

    print("Limits: %s per topic, %s per query" % (lpt, lpq))

    for t, qs in tqs.items():
        print("Topic: %s" % t)
        total_per_topic = 0
        for q in qs:
            total_per_query = 0
            for item in get_news_items(t, q):
                title = item.title
                if title in titles_seen:
                    print("-> skipping: %s" % title)
                    continue

                articles.append(item)
                titles_seen.add(title)

                total_per_topic += 1
                total_per_query += 1

                if lpq and total_per_query >= lpq:
                    print("-> query limit reached: '%s'" % q)
                    break

                if lpt and total_per_topic >= lpt:
                    print("-> [XXX] topic limit reached: '%s'" % t)
                    break

            if lpt and total_per_topic >= lpt:
                print("-> [XXX] topic limit reached: '%s'" % t)
                break

    return articles


########## MAIN ###########

def main(out_filename, lpt, lpq):
    articles = update(topic_queries, lpt, lpq)
    save_as_html(out_filename, articles)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: %s <output filename> [<limit per topic>] [<limit per query>]" % sys.argv[0])
        sys.exit(1)

    lpt = LIMIT_RESULTS_PER_TOPIC
    if len(sys.argv) > 2:
        lpt = int(sys.argv[2])

    lpq = LIMIT_RESULTS_PER_QUERY
    if len(sys.argv) > 3:
        lpq = int(sys.argv[3])

    main(sys.argv[1], lpt, lpq)
