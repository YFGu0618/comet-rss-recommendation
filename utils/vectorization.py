#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Yifan Gu <YFGu0618@outlook.com>"


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
    for uid, text in docs.items():
        tokens = word_tokenize(text)
        tokens = [ps.stem(t.lower()) for t in tokens if t not in stop]
        count = {}
        for token in tokens:
            if token in count:
                count[token] += 1
            else:
                count[token] = 1
        vectors[uid] = count
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
        for uid in vectors.keys():
            for token in vectors[uid].keys():
                vectors[uid][token] = vectors[uid][token] / \
                    (idf[token] if token in idf else 1)
        return vectors
    else:
        print("> Invalid algorithm! Please use one of the following:")
        print(">   count")
        print(">   tf-idf")
        return None
