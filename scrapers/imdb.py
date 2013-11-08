#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib2
import sys

show = sys.argv[1]
html = urllib2.urlopen("http://www.imdb.com/title/{0}".format(show))
source = html.read()
soup = BeautifulSoup(source)

rating_elements = soup.find_all('div', 'titlePageSprite star-box-giga-star')
print rating_elements[0].contents[0]
