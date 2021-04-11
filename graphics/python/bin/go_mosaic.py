#!/usr/local/bin/python3

import os
import sys

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

from mosaic import get_parser
from mosaic import save_figure
from mosaic import get_data

def square_mosaic_gradient(mode, output, n, cmap, size, dpi, interpolation, *args, **kwargs):
    data = get_data(mode, n, *args, **kwargs)
    save_figure(data, output, cmap, size, dpi, interpolation)

def square_it_up():
    parser = get_parser()

    parser.add_argument("--bug", help="change one thing (only for odd n's)", action="store_true",
            default=False)

    args = parser.parse_args()

    tech_spec_name = "-".join(filter(None,(
        args.mode,
        "%d" % args.n,
        "%dx%dinch" % args.size,
        "%ddpi" % args.dpi,
        args.cmap,
        args.interpolation,
        "bug" if args.bug else ""
    )))

    if args.tsn:
        filename, ext = os.path.splitext(args.output)
        args.output = "%s-%s%s" % (filename, tech_spec_name, ext)

    print(tech_spec_name)
    square_mosaic_gradient(args.mode, args.output, args.n, args.cmap, args.size, args.dpi,
            args.interpolation, bug=args.bug)

if __name__ == "__main__":
    square_it_up()

