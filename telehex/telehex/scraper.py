#!/usr/bin/env python
"""
TV show Scraper Class
"""
from bs4 import BeautifulSoup
from models import TVEpisode, TVShow
import urllib2
from datetime import datetime
import re
import string
import collections

API_KEY = ''
TVDB_BANNER_URL = 'http://thetvdb.com/banners/'
TVDB_SEARCH_URL = "http://thetvdb.com/api/GetSeries.php?seriesname={0}"

class Scraper:

    # Scraper Constructor
    def __init__(self, tvdb_id):
        self.tvdb_id = tvdb_id
        self.tvdbxml = urllib2.urlopen("http://thetvdb.com/api/{0}/series/{1}/all/en.xml".format(API_KEY, self.tvdb_id))
        self.tvdbsoup = BeautifulSoup(self.tvdbxml.read(), 'xml')
        
        exclude_chars = set(string.punctuation)
        self.slug = ''.join(char for char in self.tvdbsoup.SeriesName.string if char not in exclude_chars)
        self.slug = re.sub(r'\W+', '_', self.slug.lower())

        self.get_series_info()
        self.get_episode_info()

    def get_series_info(self):
        tv_show = TVShow( key_name = str(self.tvdb_id),
                title = str(self.tvdbsoup.SeriesName.string),
                desc = str(self.tvdbsoup.Overview.string),
                rating = float(self.get_imdb_rating(self.tvdbsoup.IMDB_ID.string)),
                fanart = TVDB_BANNER_URL + str(self.tvdbsoup.fanart.string),
                genre = str(self.tvdbsoup.Genre.string),
                status = str(self.tvdbsoup.Status.string),
                imdb_id = str(self.tvdbsoup.IMDB_ID.string),
                url_string = str(self.slug)).put()
        self.series_key = tv_show # obtain the key for the TV show
        
    def get_episode_info(self):
        ratings = collections.defaultdict(dict)
        if self.tvdbsoup.IMDB_ID.string:
            imdbhtml = urllib2.urlopen("http://www.imdb.com/title/{0}/epdate".format(self.tvdbsoup.IMDB_ID.string))
            imdbsoup = BeautifulSoup(imdbhtml.read())
            ratingrows = imdbsoup.select('#tn15content table')[0].select('tr')[1:]
            for ratingrow in ratingrows:
                tdlist = ratingrow.find_all('td')
                rating = tdlist[2].string
                print tdlist[2].string
                #title = re.sub('title/', '', tdlist[1].a.get('href').strip('/'))
                sep = tdlist[0].string.split('&')[0].encode('ascii', 'ignore').split('.')
                ratings[sep[0]][sep[1]] = rating.encode('ascii', 'ignore')

        episodes = self.tvdbsoup.find_all('Episode')

        for episode in episodes:
            if episode.SeasonNumber.string != '0' and episode.FirstAired.string:
                ep_rating, overview = None, None;
                #if episode.IMDB_ID.string in ratings: ep_rating = float(ratings[episode.IMDB_ID.string])
                ep_rating = float(ratings[episode.SeasonNumber.string][episode.EpisodeNumber.string])
                if episode.Overview.string: overview = str(episode.Overview.string.encode('ascii', 'ignore'))

                if episode.EpisodeName.string :
                    epname = str(episode.EpisodeName.string.encode('ascii', 'ignore'))
                else:
                    epname = "Not Available"

                TVEpisode(  parent = self.series_key,
                            key_name = str(episode.id.string),
                            name = epname,
                            season = int(episode.SeasonNumber.string),
                            desc =  overview,
                            ep_number = int(episode.EpisodeNumber.string),
                            thumb = str(episode.filename.string),
                            airdate = datetime.strptime(episode.FirstAired.string,  '%Y-%m-%d'),
                            rating = ep_rating,
                            imdb_id = str(episode.IMDB_ID.string)).put()


    def get_url_slug(self):
        return self.slug

    def get_imdb_rating(self, imdb_id):
        if imdb_id:
            html = urllib2.urlopen("http://m.imdb.com/title/{0}".format(imdb_id))
            soup = BeautifulSoup(html.read())
            rating_elements = soup.find("p", {"class":"votes"})
            return rating_elements.strong.string
        else:
            return -1

class Search:
    def search_tvdb(self, query):
        searchsoup = BeautifulSoup( urllib2.urlopen(TVDB_SEARCH_URL.format(urllib2.quote(query))).read(), 'xml')

        results = []
        for series in searchsoup.find_all('Series'):
            if series.Overview:
               desc = series.Overview.string
            else:
               desc = "Not Available"

            results.append( {
                'tvdb_id': series.seriesid.string,
                'name': series.SeriesName.string,
                'desc': desc,
            })

        return results

