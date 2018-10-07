#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Yifan Gu <YFGu0618@outlook.com>"

import os
import sys
import getopt

DATA_DIR = "data"
RSS_BASE = "http://halley.exp.sis.pitt.edu/comet/utils/_rss.jsp"
DB_START_DATE = "2008-01"
DB_END_DATE = "2018-12"
VEC_ALGO = "tfidf"  # words, count, tfidf
USER = 0
REC_START_DATE = "2008-01"
REC_END_DATE = "2018-12"
REC_ALGO = "cosine"  # euclidean, manhattan, minkowski, cosine, jaccard


class YMItr:
    """The Year-Month Iterator class"""

    def __init__(self, start, end):
        """Initialize an object with predefined start time and end time

        Args:
            start (str): Start time of the iterator, in format of "YYYY-MM".
            end (str): End time of the iterator, in format of "YYYY-MM".
        """
        self._start_yr, self._start_mon = (int(x) for x in start.split('-', 2))
        self._end_yr, self._end_mon = (int(x) for x in end.split('-', 2))
        if self._start_mon == 1:
            self._yr, self._mon = self._start_yr - 1, 12
        else:
            self._yr, self._mon = self._start_yr, self._start_mon - 1

    def next(self):
        """Return the next month in format of "YYYY-MM"

        Returns:
            None, None: if the next month is beyond the range defined by "end".
            int, int: if there is a valid (year, month) to return.
        """
        if self._yr == self._end_yr:
            if self._mon < self._end_mon:
                self._mon += 1
            else:
                return None, None
        else:
            if self._mon == 12:
                self._yr += 1
                self._mon = 1
            else:
                self._mon += 1
        return self._yr, self._mon


def download_rss():
    import requests
    itr = YMItr(DB_START_DATE, DB_END_DATE)
    yr, mon = itr.next()
    while yr and mon:
        file_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), DATA_DIR, "{:04d}-{:02d}.xml".format(yr, mon))
        if not os.path.isfile(file_path):
            response = requests.get(
                RSS_BASE + "?month={}&year={}".format(mon, yr))
            with open(file_path, "wb") as xmlfile:
                xmlfile.write(response.content)
        yr, mon = itr.next()


def generate_vector():
    directory = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), DATA_DIR)
    print(directory)
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            # TODO: Implement vector generating algorithms
            continue
        else:
            continue


def get_recommend():
    # TODO: Implement recommendation algorithms
    pass


def main(argv):
    # Getting options from command line input
    try:
        opts, _ = getopt.getopt(
            argv, "hdg:r:u:s:e:m:", ["download", "generate=", "recommend=", "user=", "start=", "end="])
    except getopt.GetoptError:
        print("> Wrong options provided!\n> Try './comet_rss -h' for help.\n")
        sys.exit(2)
    finally:
        if not opts:
            print("> Wrong options provided!\n> Try './comet_rss -h' for help.\n")
            sys.exit(2)

    # Processing options
    op = -1
    for opt, arg in opts:
        if opt == '-h':
            # Print help
            print("> Usage: ./comet_rss.py [OPTION] ...")
            print("> Options:")
            print("    -h                                print this help.")
            print("    -d, --download                    download rss data")
            print("    -g <algo>, --generate=<algo>      generate vectors using <algo>")
            print("    -r <algo>, --recommend=<algo>     recommend using <algo>")
            print("    -u <uid>, --user=<uid>            using user <uid>'s bookmarked")
            print("    -s <yyyy-mm>, --start=<yyyy-mm>   the start of time range")
            print("    -e <yyyy-mm>, --end=<yyyy-mm>     the end of time range")
            print("> Examples:")
            print("    # Download the complete dataset")
            print("    ./comet_rss -d")
            print("    # Generate document vectors using TF-IDF")
            print("    ./comet_rss -g tfidf")
            print("    # Top10 for user 1234 in 2018 using cosine similarity")
            print("    ./comet_rss -r cosine -u 1234 -s 2018-01 -e 2018-12")
        elif opt in ("-d", "--download"):
            op = 0
        elif opt in ("-g", "--generate"):
            op = 1
            VEC_ALGO = arg
        elif opt in ("-r", "--recommend"):
            op = 2
            REC_ALGO = arg
        elif opt in ("-u", "--user"):
            USER = arg
        elif opt in ("-s", "--start"):
            REC_START_DATE = arg
        elif opt in ("-e", "--end"):
            REC_END_DATE = arg

    # Start processing request
    if op == -1:
        print("> No action defined! Please try -d, -g, -r or -h for help.")
        sys.exit(2)
    elif op == 0:
        print("> Downloading data...")
        download_rss()
    elif op == 1:
        print("> Generating vectors using <{}> ...".format(VEC_ALGO))
        generate_vector()
    elif op == 2:
        print("> Calculating recommendations for user <{}> using <{}>...".format(
            USER, REC_ALGO))
        get_recommend()


if __name__ == "__main__":
    main(sys.argv[1:])
