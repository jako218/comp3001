#!/usr/bin/env python
from bs4 import BeautifulSoup
import urllib2
import sys

showid = sys.argv[1]
html = urllib2.urlopen("http://m.imdb.com/title/{0}".format(showid))
soup = BeautifulSoup(html.read())
rating_elements = soup.find("p", {"class":"votes"})
print rating_elements.strong.string