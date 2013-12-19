#!/usr/bin/env python
"""
TV show Scraper Class
"""
from bs4 import BeautifulSoup
from google.appengine.ext import db
from models import TVEpisode, TVShow, HexImages
from hexagon import Hexagon
from httplib import HTTPException
from google.appengine.api import urlfetch
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
        # Increase the timeout for fetching a url
        urlfetch.set_default_fetch_deadline(60)

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
            try:
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
            except HTTPException:
                # Failed to scrape the ratings. This is normally caused by a timeout when attempting to scrape
                # large pages. Ratings not essential, so just skip collecting them
                pass

        episodes = self.tvdbsoup.find_all('Episode')

        for episode in episodes:
            if episode.SeasonNumber.text != '0' and episode.FirstAired.text:
                ep_rating, overview = -1.0, None;
                if ratings and int(episode.EpisodeNumber.text) in ratings[int(episode.SeasonNumber.text)]:
                    ep_rating = float(ratings[int(episode.SeasonNumber.text)][int(episode.EpisodeNumber.text)])
                if episode.Overview.text: overview = episode.Overview.text

                epname = episode.EpisodeName.text if episode.EpisodeName.text else "Not Available"

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
            xml = urllib2.urlopen("http://omdbapi.com/?i={0}&r=xml".format(imdb_id))
            soup = BeautifulSoup(xml.read(), 'xml')
            tv_show = soup.find('movie')
            try:
                rating = float(tv_show['imdbRating']) if tv_show else -1
            except ValueError:
                rating = -1

            return rating

        return -1

class Search:
    def search_tvdb(self, query):
        results = []
        try:
            searchsoup = BeautifulSoup( urllib2.urlopen(TVDB_SEARCH_URL.format(urllib2.quote(query))).read(), 'xml')
            for series in searchsoup.find_all('Series'):
                desc = "No Description Available"
                if series.Overview:
                   desc = series.Overview.text if len(series.Overview.text) > 1 else desc

                results.append( {
                    'tvdb_id': series.seriesid.text,
                    'name': series.SeriesName.text,
                    'desc': desc,
                })
        except Exception:
            q = db.GqlQuery("SELECT * FROM TVShow WHERE title >=:search1 AND title <:search2", search1=query, search2=query + u"\ufffd")
            series = q.run()

            for s in series:
                desc = "No Description Available" if len(s.desc) < 2 else s.desc
                results.append( {
                    'tvdb_id': s.key().name(),
                    'name': s.title,
                    'desc': desc,
                })

        return results