#!/usr/bin/env python3

import os
import sys

from bs4 import BeautifulSoup


def data_to_csv(data, fn):
    lines = []
    lines.append(",".join(list(data[0].keys())))
    for row in data:
        lines.append(",".join(['"%s"' % v for v in row.values()]))

    print(fn)
    csvf = open(fn, 'w').write("\n".join(lines))



def main(html_fn, output_csv_fn):
    html = open(html_fn).read()

    soup = BeautifulSoup(html, 'html.parser')

    # Extract Column Headers
    column_headers = [(header['id'], header.text.strip()) for header in soup.find_all('div', {'id': lambda x: x and x.startswith('ColHead')})]
    headers = dict(column_headers)

    # Extract Rows
    #rows = list(soup.find_all('div', class_='ts-table-row'))[1:]
    rows = list(soup.find_all('div', role='row'))

    all_data = []

    # Iterate through rows and extract data
    for i in range(1, len(rows)):
        row = rows[i]
        row_data = {}
        
        divs = row.find_all('div', {'class': lambda x: x and "ts-table-row-item" in x})
        #divs = row.find_all('div', {'role': lambda x: x and x == "row"})

        # iterating cells
        for div in divs:
            header = div['data-header']
            #spans = div.find_all('span', {'class': lambda x: x and 'ts-num' in x})
            spans = div.find_all('span')
            if spans:
                text = spans[0].get_text()
                if header == 'ColHead7':
                    text = spans[1].get_text()

                row_data[headers[header]] = text

        #print(row_data)
        all_data.append(row_data)

    data_to_csv(all_data, output_csv_fn)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: %s <input_leumi_table.html>" % sys.argv[0])
        sys.exit(1)

    html_fn = sys.argv[1]
    output_csv_fn = os.path.join(os.path.dirname(html_fn), os.path.splitext(os.path.basename(html_fn))[0] + ".csv")
    main(html_fn, output_csv_fn)

