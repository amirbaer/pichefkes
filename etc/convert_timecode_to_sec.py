#!/usr/local/bin/python3

import datetime
import sys

def main():
    if not len(sys.argv) == 2:
        print("usage: %s <timecode>" % sys.argv[0])
        print("timecode format: %H:%M:%S or %M:%S")
        sys.exit(1)

    timecode = sys.argv[1]
    if len(timecode.split(":")) == 2:
        timecode = "0:%s" % timecode

    time = datetime.datetime.strptime(timecode, "%H:%M:%S")
    seconds = (3600 * time.hour) + (60 * time.minute) + time.second
    print(seconds)


if __name__ == "__main__":
    main()
