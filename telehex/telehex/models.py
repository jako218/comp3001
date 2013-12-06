from google.appengine.ext import db

class TVEpisode(db.Model):
    name = db.StringProperty(required=True)
    season = db.IntegerProperty(required=True)
    desc = db.TextProperty()
    ep_number = db.IntegerProperty(required=True)
    thumb = db.StringProperty()
    airdate = db.DateProperty()
    rating = db.FloatProperty()
    imdb_id = db.StringProperty()

class TVShow(db.Model):
    title = db.StringProperty(required=True)
    desc =  db.TextProperty()
    rating = db.FloatProperty()
    fanart = db.StringProperty()
    genre = db.StringProperty()
    status = db.StringProperty(choices=set(["Ended", "Continuing", "On Hiatus", "Other"]))
    imdb_id = db.StringProperty()
    url_string = db.StringProperty(required=True)
    last_scraped = db.DateTimeProperty()

class UserSubscriptions(db.Model):
    shows = db.ListProperty(long)

class HexImages(db.Model):
    image = db.BlobProperty()
