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
    num_seasons = db.IntegerProperty()

class HexImages(db.Model):
    image = db.BlobProperty()

class UserShow(db.Model):
    user_id = db.StringProperty(required=True)
    show_id = db.IntegerProperty(required=True) 

class User(db.Model):
    email = db.EmailProperty()