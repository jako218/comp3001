#!/usr/bin/env python

from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import datetime
import urllib2
import sys

API_KEY = '6E670E6E0ADBC2E8'

show_id = sys.argv[1]
tvdbxml = urllib2.urlopen("http://thetvdb.com/api/{0}/series/{1}/all/en.xml".format(API_KEY, show_id))
tvdbsoup = BeautifulSoup(tvdbxml.read(), 'xml')

episodes = tvdbsoup.find_all('Episode')
today = datetime.today()
nextepisode = None

for episode in episodes:
    if episode.SeasonNumber.string != '0' and episode.FirstAired.string:
        print 'Name:\t{0}'.format(episode.EpisodeName.string)
        print 'Season:\t{0}'.format(episode.SeasonNumber.string)
        print 'Number:\t{0}'.format(episode.EpisodeNumber.string)
        if episode.Overview.string: print 'Description:\t{0}'.format(episode.Overview.string)
        if episode.FirstAired.string: print 'Air Date:\t{0}'.format(episode.FirstAired.string)
        if episode.filename.string: print 'Thumbnail:\thttp://thetvdb.com/banners/{0}'.format(episode.filename.string)
        if episode.IMDB_ID.string: print 'IMDB ID:\t{0}'.format(episode.IMDB_ID.string) 
        
for i in xrange(len(episodes) - 1, 0, -1):
    episode = episodes[i]
    if episode.FirstAired.string:
        if datetime.strptime(episode.FirstAired.string, '%Y-%m-%d') > today:
            nextepisode = episode
        else:
            break;

if nextepisode:
    print 'Next episode:\tS{0}E{1} - {2}\nAirs on:\t{3}'.format(
            nextepisode.SeasonNumber.string,
            nextepisode.EpisodeNumber.string,
            nextepisode.EpisodeName.string,
            nextepisode.FirstAired.string)
else:
    print 'No next episode.'

