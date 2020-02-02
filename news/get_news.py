#!/usr/local/bin/python3

import bs4
from bs4 import BeautifulSoup as soup
import urllib.parse as urlparse
from urllib.parse import urlencode
from urllib.request import urlopen
import sys

from entities import coins, verticals, selection
from news_item import Item

#### TESTING #####

coins = coins[:1]
verticals = verticals[:2]
selection = selection[:1]

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
def get_news_items(query, dewey=[]):
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
            query,
            dewey
        ))

    return news_items

def print_news(news_items):
    for item in news_items:
      print(item.title)
      print(item.link)
      print(item.date)
      print(item.query)
      print("-"*60)


def save_as_html(filename, ml):
    html = ""
    for (cn, v, cat), items in ml.items():
        html += "<br><h2>%s :: %s :: %s</h2><br>\n" % (cn, v, cat)

        if items:
            html += "<br><h4>%s</h4><br>\n" % items[0].original_query
            for item in items:
                html += '<a href="%s">%s</a><br>\n' % (item.link, item.title)

    open(filename, 'w').write(html)


def update():
    # dict: { (cn, v, cat): [item, item, ...] }
    res = {}
    titles_seen = set()
    for c in coins:
        cn = c["tickers"][0]
        for v in verticals:
            for cat, values in c.items():
                if cat not in selection:
                    continue

                for q in values:
                    fq = " ".join([q, v]) if v else q
                    res.setdefault((cn, v, cat), [])

                    for item in get_news_items(fq, [cn, v, cat]):
                        title = item.title
                        if title in titles_seen:
                            print("skipping: %s" % title)
                            continue

                        res[(cn, v, cat)].append(item)
                        titles_seen.add(title)
    return res


########## MAIN ###########

def main(out_filename):
    ml = update()
    save_as_html(out_filename, ml)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: %s <output filename>" % sys.argv[0])
        sys.exit(1)

    main(sys.argv[1])
