#!/usr/bin/env python3.9

import sys
import re
import os

if len(sys.argv) < 2:
    print("usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

fn = " ".join(sys.argv[1:]).replace("“", '"').replace("”", '"')

datetime = re.findall(r'([^ ]+) .*', fn) # datetime
tags = re.findall(r'.*\[([^\]]+)\].*', fn) # tags
location = re.findall(r'.*\(([^\)]+)\).*', fn) # location
people = re.findall(r'.*\{([^\}]+)\}.*', fn) # location
content = re.findall(r'.*\}?\]?\) "?([^"]+)"?\..+', fn) # content

datetime and print("date:", datetime[0], sep="")
tags and print("tags:", tags[0], sep="")
location and print("location:", location[0], sep="")
people and print("people:", people[0], sep="")
content and print("content:", content[0], sep="")



