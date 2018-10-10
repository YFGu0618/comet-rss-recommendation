#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Yifan Gu <YFGu0618@outlook.com>"


class CometTalk:
    """The CoMeT talk class

    The model for CoMeT including several main fields.
    """

    def __init__(self, url='', uid=-1, title='', speaker='', date='', location='', details='', pub_date='', author=''):
        self.url = url
        self.uid = uid
        self.title = title
        self.speaker = speaker
        self.date = date
        self.location = location
        self.details = details
        self.pub_date = pub_date
        self.author = author

    def __str__(self):
        return "{}\n  Speaker: {}\n  Location: {}\n  Date: {}\n  URL: {}\n".format(
            self.title,
            self.speaker,
            self.location,
            self.date,
            self.url
        )


class XML2Talk:
    """The XML to CoMeT talk class

    Used for dealing with RSS feeds.
    """

    def __init__(self, xmlfile, encoding='utf-8'):
        self.xmlfile = xmlfile
        self.encoding = encoding

    def get_talks(self):
        import re
        from lxml import etree

        parser = etree.XMLParser(encoding=self.encoding, recover=True)
        tree = etree.parse(self.xmlfile, parser=parser)
        root = tree.getroot()
        for xmlitem in root.findall(r'./channel/item'):
            for child in xmlitem:
                if child.tag == r'link':
                    url = child.text
                    uid = re.match('.*?([0-9]+)$', url).group(1)
                elif child.tag == r'title':
                    title = child.text
                elif child.tag == r'pubDate':
                    pub_date = child.text
                elif child.tag == r'description':
                    match_groups = re.match(
                        '.*?Speaker:(.+)Date:(.+)Location:(.+)Detail:(.+)', child.text)
                    if not match_groups:
                        continue
                    speaker = match_groups.group(1)
                    date = match_groups.group(2)
                    location = match_groups.group(3)
                    details = match_groups.group(4)
                elif child.tag == r'author':
                    author = child.text
            yield CometTalk(url, int(uid), title, speaker, date, location, details, pub_date, author)


def main():
    a = XML2Talk(xmlfile='../data/2018-10.xml', encoding='cp1252')
    for talk in a.get_talks():
        print(str(talk))


if __name__ == '__main__':
    main()
