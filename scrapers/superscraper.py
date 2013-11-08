#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib2
import sys

API_KEY = '6E670E6E0ADBC2E8'

show_id = sys.argv[1]
tvdbxml = urllib2.urlopen("http://thetvdb.com/api/{0}/series/{1}/all/en.xml".format(API_KEY, show_id))
tvdbsoup = BeautifulSoup(tvdbxml.read(), 'xml')

print 'Title:\t' + tvdbsoup.find('SeriesName').string
print 'Description:\t' + tvdbsoup.find('Overview').string
print 'Fanart:\t' + tvdbsoup.find('fanart').string
print 'Genre:\t' + tvdbsoup.find('Genre').string
print 'Status:\t' + tvdbsoup.find('Status').string

imdb_id = tvdbsoup.find('IMDB_ID').string
print 'IMDB ID:\t' + imdb_id

imdbhtml = urllib2.urlopen("http://www.imdb.com/title/{0}".format(imdb_id))
imdbsoup = BeautifulSoup(imdbhtml.read())

rating_elements = imdbsoup.find_all('div', 'titlePageSprite star-box-giga-star')
print 'IMDB Rating:\t' + rating_elements[0].string
