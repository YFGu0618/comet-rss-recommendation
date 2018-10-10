#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Yifan Gu <YFGu0618@outlook.com>"

import os
import sys
import getopt

DATA_DIR = 'data'
RSS_BASE = 'http://halley.exp.sis.pitt.edu/comet/utils/_rss.jsp'


def download_rss(start_date='2008-01', end_date='2018-12'):
    import urllib3
    from models.YearMonth import YearMonth

    ym = YearMonth(start_date, end_date)
    yr, mon = ym.next()
    http = urllib3.PoolManager()
    while yr and mon:
        file_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), DATA_DIR, '{:04d}-{:02d}.xml'.format(yr, mon))
        if not os.path.isfile(file_path):
            r = http.request('GET', RSS_BASE +
                             '?month={}&year={}'.format(mon, yr))
            with open(file_path, 'wb') as f:
                f.write(r.data)
        yr, mon = ym.next()


def generate_vector(algo='tf-idf'):
    import json
    from utils.vectorization import vectorize
    from models.CometTalk import XML2Talk

    # Parse talks from available data
    directory = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), DATA_DIR)
    talks = {}
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            rss = XML2Talk(os.path.join(
                directory, filename), encoding='cp1252')
            for t in rss.get_talks():
                if t.uid not in talks:
                    talks[t.uid] = " ".join(
                        [t.title, t.speaker, t.date, t.location, t.details])
    if len(talks) < 1:
        print("> Data not available! Try downloading data first.")
        sys.exit(2)

    # Vectorize talks and store result
    vectors = vectorize(talks, algo)
    if vectors:
        vec_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '{}.vec'.format(algo))
        with open(vec_path, 'w', encoding='utf-8') as f:
            for talk_id, vector in vectors.items():
                f.write("{}\t{}\n".format(talk_id, json.dumps(vector)))
            print("> Total {} talks vectorized. See <{}> for more details.".format(
                len(vectors), '{}.vec'.format(algo)))


def get_recommend(user, algo='cosine'):
    import json
    import urllib3
    from utils.similarity import sim_score
    from utils.vectorization import vectorize
    from models.CometTalk import XML2Talk

    # Download user bookmarked talks
    http = urllib3.PoolManager()
    r = http.request('GET', RSS_BASE + '?v=bookmark&user_id={}'.format(user))
    with open('uid{}.xml'.format(user), 'wb') as f:
        f.write(r.data)

    # Parsing xml and tokenize all talks
    user_components = []
    rss = XML2Talk('uid{}.xml'.format(user), encoding='cp1252')
    for t in rss.get_talks():
        user_components += [t.title, t.speaker, t.date, t.location, t.details]
    user_vec = vectorize({user: " ".join(user_components)}, algo='count')[user]

    if len(user_vec) < 1:
        print("> Data not available for user! Try another user.")
        sys.exit(2)

    # Calculate similarity score between user and each talks
    directory = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(directory):
        if filename.endswith('.vec'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    k, v = line.split('\t')
                    doc_vec = json.loads(v)
                    print("{0:.5f}".format(
                        sim_score(user_vec, doc_vec, algo)), k)


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
            print("    ./comet_rss -g tf-idf")
            print("    # Recommendations for user 1234 in 2018 using cosine similarity")
            print("    ./comet_rss -r cosine -u 1234 -s 2018-01 -e 2018-12")
            sys.exit(0)
        elif opt in ('-d', '--download'):
            op = 0
        elif opt in ('-g', '--generate'):
            op = 1
            vec_algo = arg
        elif opt in ('-r', '--recommend'):
            op = 2
            rec_algo = arg
        elif opt in ('-u', '--user'):
            user = arg
        elif opt in ('-s', '--start'):
            REC_START_DATE = arg
        elif opt in ('-e', '--end'):
            REC_END_DATE = arg

    # TODO: start time and end time currently not used

    # Start processing request
    if op == -1:
        print("> No action defined! Please try -d, -g, -r or -h for help.")
        sys.exit(2)
    elif op == 0:
        print("> Downloading data...")
        download_rss()
    elif op == 1:
        print("> Generating vectors using <{}> ...".format(vec_algo))
        generate_vector(algo=vec_algo)
    elif op == 2:
        print("> Calculating recommendations for user <{}> using <{}>...".format(
            user, rec_algo))
        get_recommend(user=user, algo=rec_algo)


if __name__ == '__main__':
    main(sys.argv[1:])
