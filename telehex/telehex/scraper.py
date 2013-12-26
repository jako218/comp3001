"""
:mod:`scraper` -- Performs the Scraping
=================================================

.. module:: scraper
   :synopsis: A collection of classes which perform the scraping for telehex

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

# GAE Imports
from google.appengine.ext import db
from google.appengine.api import urlfetch

# Telehex Imports
from models import TVEpisode, TVShow, HexImages
from hexagon import Hexagon

# Other Imports
from bs4 import BeautifulSoup
from httplib import HTTPException
from datetime import datetime
import urllib2
import re
import string
import collections

API_KEY = ''
TVDB_BANNER_URL = 'http://thetvdb.com/banners/'
TVDB_SEARCH_URL = "http://thetvdb.com/api/GetSeries.php?seriesname={0}"


class Scraper:
    """
    A Class used to perform the scraping for the TVShows and TVEpisodes
    """

    def __init__(self, tvdb_id):
        """
        The :class:Scraper class constructor. Takes a tvdb_id and initialises the scraping for the TVShow
        and the TVEpisodes

        :param tvdb_id: The tvdb id was the show to be scraped.
        """

        # Increase the timeout for fetching a url - required for large shows
        urlfetch.set_default_fetch_deadline(60)

        self.tvdb_id = tvdb_id

        # Fetch the XML from tvdb and turn into a BeautifulSoup Object
        self.tvdbxml = urllib2.urlopen("http://thetvdb.com/api/{0}/series/{1}/all/en.xml".format(API_KEY, self.tvdb_id))
        self.tvdbsoup = BeautifulSoup(self.tvdbxml.read(), 'xml')

        # Generate the show slug for the show, e.g. Breaking Bad becomes breaking_bad
        exclude_chars = set(string.punctuation)
        self.slug = ''.join(char for char in self.tvdbsoup.SeriesName.text if char not in exclude_chars)
        self.slug = re.sub(r'\W+', '_', self.slug.lower())

        # Perform the scraping for the TVShow
        self.get_series_info()

        # Perform the scraping for the TVEpisodes
        self.get_episode_info()

        # Specify when the show was last scraped
        q = TVShow.get_by_key_name(self.tvdb_id)
        q.last_scraped = datetime.now()
        q.put()

    def get_series_info(self):
        """
        Gets the Series info for a TVShow and puts it into the GAE Datastore.
        The information which is scraped includes show rating, show name, show description and show status.
        """

        # Generate the fanart URL if fanart exists. This is used later to generate the Hexagon image for the show
        fanart_url = TVDB_BANNER_URL + self.tvdbsoup.fanart.text if self.tvdbsoup.fanart.text else None

        # Identify the show genres
        genres = self.tvdbsoup.Genre.text.split("|")

        # Put the scraped information into the GAE datastore
        tv_show = TVShow(key_name=self.tvdb_id,
                         title=self.tvdbsoup.SeriesName.text,
                         desc=self.tvdbsoup.Overview.text,
                         rating=float(self.get_imdb_rating(self.tvdbsoup.IMDB_ID.text)),
                         fanart=fanart_url,
                         genre=genres[1],
                         subgenre=genres[2],
                         status=self.tvdbsoup.Status.text,
                         imdb_id=self.tvdbsoup.IMDB_ID.text,
                         url_string=self.slug,
                         last_scraped=datetime.utcfromtimestamp(0),
                         num_seasons=int(self.tvdbsoup.find_all('SeasonNumber')[-1].text) if self.tvdbsoup.find_all(
                             'SeasonNumber') else 0
        ).put()

        # Obtain the key for the TVShow
        self.series_key = tv_show

        # If fanart exists generate a hexagon image and store in the datastore
        if fanart_url:
            HexImages(parent=self.series_key,
                      key_name=self.tvdb_id,
                      image=db.Blob(Hexagon(fanart_url).get_hex())
            ).put()

    def get_episode_info(self):
        """
        Gets the episode info for a TVShow and puts it into the GAE Datastore.
        """

        # Create a ratings dictionary
        ratings = collections.defaultdict(dict)

        # If the show has an IMDB id, try and grab the episode ratings for this show
        if self.tvdbsoup.IMDB_ID.text:
            try:
                # Turn the IMDB ratings pages into a BeautifulSoup Object, allowing particular page elements to be grabbed
                imdbhtml = urllib2.urlopen("http://www.imdb.com/title/{0}/epdate".format(self.tvdbsoup.IMDB_ID.text))
                imdbsoup = BeautifulSoup(imdbhtml.read())

                # Identify the episode ratings and store in the ratings dictionary
                if imdbsoup.select('#tn15content table'):

                    # Find all the rows in the ratings table - each row corresponds to an episode with a rating
                    ratingrows = imdbsoup.select('#tn15content table')[0].select('tr')[1:]

                    # For each row identify the season number, episode number and the rating
                    for ratingrow in ratingrows:
                        tdlist = ratingrow.find_all('td')
                        rating = tdlist[2].text

                        # Identify the season and episode (sep)
                        sep = tdlist[0].text.split('&')[0].split('.')

                        # Try and store the rating into the dictionary - occasionally rating is a string e.g. N/A so
                        # ValueError is caught to allow scraping to continue
                        try:
                            #
                            ratings[int(sep[0])][int(sep[1])] = rating
                        except ValueError:
                            continue
            except HTTPException:
                # Failed to scrape the ratings. This is normally caused by a timeout when attempting to scrape
                # large pages. Ratings not essential, so just skip collecting them
                pass

        # From the tvdb BeautifulSoup object, grab all the episodes
        episodes = self.tvdbsoup.find_all('Episode')

        # Loop through all the episodes and store the information into the GAE datastore
        for episode in episodes:

            # Check that this is a proper episode - don't want to display web-episodes, etc.
            if episode.SeasonNumber.text != '0' and episode.FirstAired.text:

                # Check if this episode has a rating, otherwise it is left at -1.0 to signify no rating
                ep_rating = -1.0
                if ratings and int(episode.EpisodeNumber.text) in ratings[int(episode.SeasonNumber.text)]:
                    ep_rating = float(ratings[int(episode.SeasonNumber.text)][int(episode.EpisodeNumber.text)])

                overview = episode.Overview.text if episode.Overview.text else None
                epname = episode.EpisodeName.text if episode.EpisodeName.text else "Not Available"

                try:
                    airdate = datetime.strptime(episode.FirstAired.text, '%Y-%m-%d').date()
                except ValueError:
                    airdate = None

                # Put the TVEpisode into the datastore
                TVEpisode(parent=self.series_key,
                          key_name=episode.id.text,
                          name=epname,
                          season=int(episode.SeasonNumber.text),
                          desc=overview,
                          ep_number=int(episode.EpisodeNumber.text),
                          thumb=episode.filename.text,
                          airdate=airdate,
                          rating=ep_rating,
                          imdb_id=episode.IMDB_ID.text
                ).put()


    def get_url_slug(self):
        """
        Returns the shows url slug - e.g. Breaking Bad's slug is breaking_bad

        :return: the url slug for this scraping instance
        """
        return self.slug

    def get_imdb_rating(self, imdb_id):
        """
        Gets the IMDB rating for the TVShow

        :param imdb_id: the IMDB id of the TVShow
        :return: The rating of the show if it exists, otherwise -1 if the show has no rating
        """
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
    """
    A Class used to perform a Search. Makes use of The TVDB's search API
    """

    def search_tvdb(self, query):
        """
        Performs a search using The TVDB search API. If the API is not live, a fallback search is used which makes use
        of the items already within the datastore

        :param query: The Search Query
        :return: A list of the search results, with each element being a dictionary containing the id, name and desc of
        the show
        """

        results = []
        try:
            # Use the tvdb to provide the search results
            searchsoup = BeautifulSoup(urllib2.urlopen(TVDB_SEARCH_URL.format(urllib2.quote(query))).read(), 'xml')

            # Populate the list of search results, each item in the list is a dictionary containing the id, name and desc
            # of the tv show
            for series in searchsoup.find_all('Series'):
                desc = "No Description Available"
                if series.Overview:
                    desc = series.Overview.text if len(series.Overview.text) > 1 else desc

                results.append({
                    'tvdb_id': series.seriesid.text,
                    'name': series.SeriesName.text,
                    'desc': desc,
                })

        except IOError:
            # Use the datastore to provide the search results
            q = db.GqlQuery("SELECT * FROM TVShow WHERE title >=:search1 AND title <:search2", search1=query,
                            search2=query + u"\ufffd")
            series = q.run()

            for s in series:
                desc = "No Description Available" if len(s.desc) < 2 else s.desc
                results.append({
                    'tvdb_id': s.key().name(),
                    'name': s.title,
                    'desc': desc,
                })

        return results
