#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Yifan Gu <YFGu0618@outlook.com>"

import os
import sys
import getopt

DATA_DIR = 'data'
RSS_BASE = 'http://halley.exp.sis.pitt.edu/comet/utils/_rss.jsp'


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


def download_rss(start_date='2008-01', end_date='2018-12'):
    import urllib3
    itr = YMItr(start_date, end_date)
    yr, mon = itr.next()
    http = urllib3.PoolManager()
    while yr and mon:
        file_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), DATA_DIR, '{:04d}-{:02d}.xml'.format(yr, mon))
        if not os.path.isfile(file_path):
            r = http.request('GET', RSS_BASE +
                             '?month={}&year={}'.format(mon, yr))
            with open(file_path, 'wb') as f:
                f.write(r.data)
        yr, mon = itr.next()


def vectorize(docs, algo='tf-idf'):
    import string
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    # Ensure data used by nltk is available
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    # The filter for stopwords and punctuations
    stop = stopwords.words('english') + list(string.punctuation)
    ps = PorterStemmer()
    vectors = {}
    idf = {}
    # Count tf and idf for each doc
    for doc in docs:
        tokens = word_tokenize(doc['title']) + \
            word_tokenize(doc['description'])
        tokens = [ps.stem(t.lower()) for t in tokens if t not in stop]
        count = {}
        for token in tokens:
            if token in count:
                count[token] += 1
            else:
                count[token] = 1
        vectors[doc['id']] = count
        for k in count.keys():
            if k in idf:
                idf[k] += 1
            else:
                idf[k] = 1
    # return vectors correspond to defined algorithm
    if algo == 'count':
        return vectors
    elif algo == 'tf-idf':
        # Count document frequency
        for docid in vectors.keys():
            for token in vectors[docid].keys():
                vectors[docid][token] = vectors[docid][token] / \
                    (idf[token] if token in idf else 1)
        return vectors
    else:
        print("> Invalid algorithm! Please use one of the following:")
        print(">   count")
        print(">   tf-idf")
        return None


def generate_vector(algo='tf-idf'):
    import json
    import re
    from lxml import etree

    parser = etree.XMLParser(encoding='cp1252', recover=True)
    talks = []
    directory = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), DATA_DIR)
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            tree = etree.parse(os.path.join(
                directory, filename), parser=parser)
            root = tree.getroot()
            for item in root.findall('./channel/item'):
                talk = {}
                for child in item:
                    # title, pubDate, link, {http://purl.org/rss/1.0/modules/content/}encoded, description, author
                    if child.tag == 'link':
                        talk_id = re.match('.*?([0-9]+)$', child.text).group(1)
                        talk['id'] = talk_id
                    if child.tag == 'title':
                        talk['title'] = child.text
                    elif child.tag == 'description':
                        talk['description'] = child.text
                if all(k in talk for k in ('id', 'title', 'description')):
                    talks.append(talk)
            continue
        else:
            continue
    if len(talks) < 1:
        print("> Data not available! Try downloading data first.")
        sys.exit(2)
    vectors = vectorize(talks, algo)
    if vectors:
        vec_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '{}.vec'.format(algo))
        with open(vec_path, 'w', encoding='utf-8') as f:
            for talk_id, vector in vectors.items():
                f.write("{}\t{}\n".format(talk_id, json.dumps(vector)))
            print("> Total {} talks vectorized. See <{}> for more details.".format(
                len(vectors), '{}.vec'.format(algo)))


def sim_score(vec1, vec2, algo='cosine'):
    import math
    dims = list(vec1.keys()) + list(vec2.keys())
    if algo == 'cosine':
        sum_ab = 0
        sum_aa = 0
        sum_bb = 0
        for dim in dims:
            a = vec1[dim] if dim in vec1 else 0
            b = vec2[dim] if dim in vec2 else 0
            sum_ab += a * b
            sum_aa += a * a
            sum_bb += b * b
        return sum_ab / (math.sqrt(sum_aa) * math.sqrt(sum_bb))
    elif algo == 'euclidean':
        sum_sq = 0
        for dim in dims:
            a = vec1[dim] if dim in vec1 else 0
            b = vec2[dim] if dim in vec2 else 0
            sum_sq += (a - b) ** 2
        return math.sqrt(sum_sq)
    elif algo == 'manhattan':
        sum_dist = 0
        for dim in dims:
            a = vec1[dim] if dim in vec1 else 0
            b = vec2[dim] if dim in vec2 else 0
            sum_dist += abs(a - b)
        return sum_dist
    elif algo == 'jaccard':
        intersect = [dim for dim in vec1.keys() if dim in vec2.keys()]
        return len(intersect) / len(dims)
    else:
        print("> Invalid algorithm! Please use one of the following:")
        print(">   cosine")
        print(">   euclidean")
        print(">   manhattan")
        print(">   jaccard")
        return None


def get_recommend(user, algo='cosine'):
    import json
    import nltk
    import string
    import urllib3
    from lxml import etree
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    # Ensure data used by nltk is available
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    stop = stopwords.words('english') + list(string.punctuation)
    ps = PorterStemmer()
    # Download user bookmarked talks
    http = urllib3.PoolManager()
    r = http.request('GET', RSS_BASE + '?v=bookmark&user_id={}'.format(user))
    with open('uid{}.xml'.format(user), 'wb') as f:
        f.write(r.data)
    # Parsing xml and tokenize all talks
    parser = etree.XMLParser(encoding='cp1252', recover=True)
    tree = etree.parse('uid{}.xml'.format(user), parser=parser)
    root = tree.getroot()
    tokens = []
    for item in root.findall('./channel/item'):
        for child in item:
            if child.tag == 'title':
                tokens += word_tokenize(child.text)
            elif child.tag == 'description':
                tokens += word_tokenize(child.text)
    tokens = [ps.stem(t.lower()) for t in tokens if t not in stop]
    if len(tokens) < 1:
        print("> Data not available for user <{}>! Try another id.".format(user))
        sys.exit(2)
        # Calculate the vector for user
    user_vec = {}
    for token in tokens:
        if token in user_vec:
            user_vec[token] += 1
        else:
            user_vec[token] = 1
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
            print("    # Top10 for user 1234 in 2018 using cosine similarity")
            print("    ./comet_rss -r cosine -u 1234 -s 2018-01 -e 2018-12")
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
