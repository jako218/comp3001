#!/usr/bin/env python
"""
TV show Scraper Class
"""
from bs4 import BeautifulSoup
from models import TVEpisode, TVShow
import urllib2
from datetime import datetime
import re

API_KEY = '6E670E6E0ADBC2E8'

class Scraper:

    # Scraper Constructor
    def __init__(self, tvdb_id):
        self.tvdb_id = tvdb_id
        self.tvdbxml = urllib2.urlopen("http://thetvdb.com/api/{0}/series/{1}/all/en.xml".format(API_KEY, self.tvdb_id))
        self.tvdbsoup = BeautifulSoup(self.tvdbxml.read(), 'xml')
        self.get_series_info()
        self.get_episode_info()

    def get_series_info(self):
        tv_show = TVShow( key_name = str(self.tvdb_id),
                title = str(self.tvdbsoup.SeriesName.string),
                desc = str(self.tvdbsoup.Overview.string),
                rating = float(self.get_imdb_rating(self.tvdbsoup.IMDB_ID.string)),
                genre = str(self.tvdbsoup.Genre.string),
                status = str(self.tvdbsoup.Status.string),
                imdb_id = str(self.tvdbsoup.IMDB_ID.string)).put()
        self.series_key = tv_show # obtain the key for the TV show
        
    def get_episode_info(self):
        ratings = {}
        if self.tvdbsoup.IMDB_ID.string:
            imdbhtml = urllib2.urlopen("http://www.imdb.com/title/{0}/epdate".format(self.tvdbsoup.IMDB_ID.string))
            imdbsoup = BeautifulSoup(imdbhtml.read())
            ratingrows = imdbsoup.select('#tn15content table')[0].select('tr')[1:]
            for ratingrow in ratingrows:
                tdlist = ratingrow.find_all('td')
                rating = tdlist[2].string
                title = re.sub('title/', '', tdlist[1].a.get('href').strip('/'))
                ratings[title] = rating

        episodes = self.tvdbsoup.find_all('Episode')

        for episode in episodes:
            if episode.SeasonNumber.string != '0' and episode.FirstAired.string:
                ep_rating, overview = None, None;
                if episode.IMDB_ID.string in ratings: ep_rating = float(ratings[episode.IMDB_ID.string])
                if episode.Overview.string: overview = str(episode.Overview.string.encode('ascii', 'ignore'))

                TVEpisode(  parent = self.series_key,
                            key_name = str(episode.id.string),
                            name = str(episode.EpisodeName.string),
                            season = str(episode.SeasonNumber.string),
                            desc =  overview,
                            ep_number = int(episode.EpisodeNumber.string),
                            thumb = str(episode.filename.string),
                            airdate = datetime.strptime(episode.FirstAired.string,  '%Y-%m-%d'),
                            rating = ep_rating,
                            imdb_id = str(episode.IMDB_ID.string)).put()


    def get_imdb_rating(self, imdb_id):
        if imdb_id:
            html = urllib2.urlopen("http://m.imdb.com/title/{0}".format(imdb_id))
            soup = BeautifulSoup(html.read())
            rating_elements = soup.find("p", {"class":"votes"})
            return rating_elements.strong.string
        else:
            return -1