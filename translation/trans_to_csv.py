#!/usr/local/bin/python3

import sys
from googletrans import Translator


def get_output_filename(input_filename):
    return "%s-trans.csv" % ".".join(input_filename.split()[:-1])

def clean_text(text):
    return text
    #return text.replace('"', "'")

def main(input_filename, output_filename):
    source_text = open(input_filename).read()
    lines = list(filter(None, source_text.splitlines()))

    translator = Translator()
    output_file = open(output_filename, 'w')

    for line in lines:
        td = translator.translate(clean_text(line), dest='iw', src='en') # english -> hebrew
        output_file.write('%s\t%s\n' % (td.origin, td.text))
        sys.stdout.write(".")
        sys.stdout.flush()


    output_file.close()
    print("\ndone.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: %s <input file> <output file>" % sys.argv[0])
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    main(input_filename, output_filename)
