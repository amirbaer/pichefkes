#!/usr/local/bin/python3

from GoogleNews import GoogleNews

from news_item import Item
from entities import coins, verticals, selection

import sys

#### TESTING #####

coins = coins[:1]
verticals = verticals[:2]
selection = selection[:1]

#################


def save_as_html(filename, ml):
    html = ""
    for c in ml.keys():
        html += "<h1>%s</h1>\n" % c

        for v in ml[c].keys():
            html += "<h2>%s :: %s</h2>\n" % (c, v)

            for cat in ml[c][v].keys():
                html += "<h3>%s :: %s :: %s</h3>\n" % (c, v, cat)

                for query, items in ml[c][v][cat].items():
                    html += "<h4>%s</h4>" % query
                    for item in items:
                        html += '<a href="%s">%s</a>' % (item["link"], item["title"])
                        html += "<br>"

                html += "<br>"
            html += "<br>"
        html += "<br>"

    open(filename, 'w').write(html)


def update():
    gn = GoogleNews()
    res = {}
    titles_seen = set()
    for c in coins:
        cn = c["tickers"][0]
        res.setdefault(cn, {})

        for v in verticals:
            res[cn].setdefault(v, {})

            for cat, values in c.items():
                if cat not in selection:
                    continue
                res[cn][v].setdefault(cat, {})

                for q in values:
                    fq = " ".join([q, v]) if v else q
                    res[cn][v][cat].setdefault(fq, [])

                    # TODO: paging
                    gn.search(fq)

                    for item in gn.results:
                        title = item["title"]
                        if title in titles_seen:
                            print("skipping: %s" % title)
                            continue

                        res[cn][v][cat][fq].append(item)
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
