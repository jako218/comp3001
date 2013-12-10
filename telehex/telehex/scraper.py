#!/usr/bin/env python
"""
TV show Scraper Class
"""
from bs4 import BeautifulSoup
from google.appengine.ext import db
from models import TVEpisode, TVShow, HexImages
from hexagon import Hexagon
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
        self.slug = ''.join(char for char in self.tvdbsoup.SeriesName.text if char not in exclude_chars)
        self.slug = re.sub(r'\W+', '_', self.slug.lower())

        self.get_series_info()
        self.get_episode_info()

        q = TVShow.get_by_key_name(self.tvdb_id)
        q.last_scraped = datetime.now()
        q.put()

    def get_series_info(self):
        print self.tvdbsoup.fanart.text

        fanart_url = None
        if self.tvdbsoup.fanart.text:
            fanart_url = TVDB_BANNER_URL + self.tvdbsoup.fanart.text;

        tv_show = TVShow( key_name = self.tvdb_id,
                title = self.tvdbsoup.SeriesName.text,
                desc = self.tvdbsoup.Overview.text,
                rating = float(self.get_imdb_rating(self.tvdbsoup.IMDB_ID.text)),
                fanart = fanart_url,
                genre = self.tvdbsoup.Genre.text,
                status = self.tvdbsoup.Status.text,
                imdb_id = self.tvdbsoup.IMDB_ID.text,
                url_string = self.slug,
                last_scraped = datetime.utcfromtimestamp(0),
                num_seasons = int(self.tvdbsoup.find_all('SeasonNumber')[-1].text)
        ).put()
        self.series_key = tv_show # obtain the key for the TV show

        if fanart_url:
            HexImages(  parent = self.series_key,
                        key_name = self.tvdb_id,
                        image = db.Blob(Hexagon(fanart_url).get_hex())
            ).put()
        
    def get_episode_info(self):
        ratings = collections.defaultdict(dict)
        if self.tvdbsoup.IMDB_ID.text:
            imdbhtml = urllib2.urlopen("http://www.imdb.com/title/{0}/epdate".format(self.tvdbsoup.IMDB_ID.text))
            imdbsoup = BeautifulSoup(imdbhtml.read())
            if imdbsoup.select('#tn15content table'):
                ratingrows = imdbsoup.select('#tn15content table')[0].select('tr')[1:]
                for ratingrow in ratingrows:
                    tdlist = ratingrow.find_all('td')
                    rating = tdlist[2].text
                    sep = tdlist[0].text.split('&')[0].split('.')
                    try:
                        ratings[int(sep[0])][int(sep[1])] = rating
                    except ValueError:
                        continue

        episodes = self.tvdbsoup.find_all('Episode')

        for episode in episodes:
            if episode.SeasonNumber.text != '0' and episode.FirstAired.text:
                ep_rating, overview = -1.0, None;
                if ratings and int(episode.EpisodeNumber.text) in ratings[int(episode.SeasonNumber.text)]:
                    ep_rating = float(ratings[int(episode.SeasonNumber.text)][int(episode.EpisodeNumber.text)])
                if episode.Overview.text: overview = episode.Overview.text

                if episode.EpisodeName.text :
                    epname = episode.EpisodeName.text
                else:
                    epname = "Not Available"

                TVEpisode(  parent = self.series_key,
                            key_name = episode.id.text,
                            name = epname,
                            season = int(episode.SeasonNumber.text),
                            desc =  overview,
                            ep_number = int(episode.EpisodeNumber.text),
                            thumb = episode.filename.text,
                            airdate = datetime.strptime(episode.FirstAired.text,  '%Y-%m-%d').date(),
                            rating = ep_rating,
                            imdb_id = episode.IMDB_ID.text
                ).put()


    def get_url_slug(self):
        return self.slug

    def get_imdb_rating(self, imdb_id):
        if imdb_id:
            html = urllib2.urlopen("http://m.imdb.com/title/{0}".format(imdb_id))
            soup = BeautifulSoup(html.read())
            rating_elements = soup.find("p", {"class":"votes"})
            if rating_elements:
                return rating_elements.strong.text 
        return -1

class Search:
    def search_tvdb(self, query):
        searchsoup = BeautifulSoup( urllib2.urlopen(TVDB_SEARCH_URL.format(urllib2.quote(query))).read(), 'xml')

        results = []
        for series in searchsoup.find_all('Series'):
            if series.Overview:
               desc = series.Overview.text
            else:
               desc = "Not Available"

            results.append( {
                'tvdb_id': series.seriesid.text,
                'name': series.SeriesName.text,
                'desc': desc,
            })

        return results

