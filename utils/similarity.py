#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Yifan Gu <YFGu0618@outlook.com>"


def sim_score(v1, v2, algo='manhattan', p=1):
    """Method for calculate similarity score
    """
    import math

    # Convert vectors from dict to list of numbers
    if type(v1) is dict and type(v2) is dict:
        dims = list(v1.keys()) + list(v2.keys())
        _v1 = [v1[k] if k in v1 else 0 for k in dims]
        _v2 = [v2[k] if k in v2 else 0 for k in dims]
    else:
        _v1 = v1
        _v2 = v2

        # Calculate metrics accordingly
    if algo == 'manhattan':
        return sum(abs(a - b) for a, b in zip(_v1, _v2))
    elif algo == 'euclidean':
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(_v1, _v2)))
    elif algo == 'minkowski':
        return sum(abs(a - b) ** p for a, b in zip(_v1, _v2)) ** (1 / p)
    elif algo == 'cosine':
        for i in range(len(_v1)):
            sum11 = _v1[i] ** 2
            sum22 = _v2[i] ** 2
            sum12 = _v1[i] * _v2[i]
        return sum12 / math.sqrt(sum11 + sum22)
    elif algo == 'jaccard':
        l = len(_v1)
        inter = sum([1 if (_v1[i] > 0 and _v2[i] > 0)
                     else 0 for i in range(l)])
        return inter / l
    else:
        print("> Invalid algorithm! Please use one of the following:")
        print(">   manhattan (default)")
        print(">   euclidean")
        print(">   minkowski")
        print(">   cosine")
        print(">   jaccard")
        return None


def main():
    a = [1, 2, 3, 4, 5, 6, 7]
    b = [1, 1, 1, 1, 1, 1, 1]
    c = [1, 0, 3, 0, 5, 0, 7]

    print(a)
    print(b)
    print(c)
    print("\nSimilarity: a|b, b|c, a|c")
    print("manhattan: {:.3f}\t{:.3f}\t{:.3f}".format(
        sim_score(a, b, algo='manhattan'),
        sim_score(b, c, algo='manhattan'),
        sim_score(a, c, algo='manhattan')))
    print("euclidean: {:.3f}\t{:.3f}\t{:.3f}".format(
        sim_score(a, b, algo='euclidean'),
        sim_score(b, c, algo='euclidean'),
        sim_score(a, c, algo='euclidean')))
    print("minkowski: {:.3f}\t{:.3f}\t{:.3f}".format(
        sim_score(a, b, algo='minkowski', p=4),
        sim_score(b, c, algo='minkowski', p=4),
        sim_score(a, c, algo='minkowski', p=4)))
    print("cosine:    {:.3f}\t{:.3f}\t{:.3f}".format(
        sim_score(a, b, algo='cosine'),
        sim_score(b, c, algo='cosine'),
        sim_score(a, c, algo='cosine')))
    print("jaccard:   {:.3f}\t{:.3f}\t{:.3f}".format(
        sim_score(a, b, algo='jaccard'),
        sim_score(b, c, algo='jaccard'),
        sim_score(a, c, algo='jaccard')))


if __name__ == '__main__':
    main()
