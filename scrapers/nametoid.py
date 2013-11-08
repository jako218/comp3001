#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib2
import sys

show_name = urllib2.quote('_'.join(sys.argv[1:]))

tvdbxml = urllib2.urlopen("http://thetvdb.com/api/GetSeries.php?seriesname={0}".format(show_name))
tvdbsoup = BeautifulSoup(tvdbxml.read(), 'xml')

for hit in tvdbsoup.find_all('Series'):
    print hit.id.string

