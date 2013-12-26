"""
:mod:`models` - The models for the GAE Datastore
=================================================

.. module:: models
   :synopsis: Creates the models for the Google App Engine (GAE) datastore

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


class TVEpisode(db.Model):
    """
    The :class:TVEpisode class is used to store information about a TVEpisode for a particular :class:TVShow
    """
    name = db.StringProperty(required=True)
    season = db.IntegerProperty(required=True)
    desc = db.TextProperty()
    ep_number = db.IntegerProperty(required=True)
    thumb = db.StringProperty()
    airdate = db.DateProperty()
    rating = db.FloatProperty()
    imdb_id = db.StringProperty()


class TVShow(db.Model):
    """
    The :class:TVShow class is used to store information about a tv show
    """
    title = db.StringProperty(required=True)
    desc = db.TextProperty()
    rating = db.FloatProperty()
    fanart = db.StringProperty()
    genre = db.StringProperty()
    subgenre = db.StringProperty()
    status = db.StringProperty(choices={"Ended", "Continuing", "On Hiatus", "Other"})
    imdb_id = db.StringProperty()
    url_string = db.StringProperty(required=True)
    last_scraped = db.DateTimeProperty()
    num_seasons = db.IntegerProperty()


class HexImages(db.Model):
    """
    The :class:HexImages class is used to store images in Blob form for a :class:TVShow
    """
    image = db.BlobProperty()


class UserShow(db.Model):
    """
    The :class:UserShow class is used to store user subscriptions. Achieved by creating a one-to-one mapping between
    a user id and a show id
    """
    user_id = db.StringProperty(required=True)
    show_id = db.IntegerProperty(required=True)


class User(db.Model):
    """
    The :class:User class is used to store users email addresses if they have requested to receive a weekly email update
    """
    email = db.EmailProperty()
