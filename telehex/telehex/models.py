from google.appengine.ext import db

class Greeting(db.Model):
    """Models an individual Guestbook entry with an author, content, and date."""
    author = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def get_key_from_name(cls, guestbook_name=None):
        return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class TVEpisode(db.Model):
	name = db.StringProperty(required=True)
	season = db.StringProperty(required=True)
	desc = db.TextProperty()
	ep_number = db.IntegerProperty(required=True)
	thumb = db.StringProperty()
	airdate = db.DateTimeProperty()
	rating = db.FloatProperty()
	imdb_id = db.StringProperty()
	

class TVShow(db.Model):
	#tvdb_id = db.IntegerProperty(required=True)
	title = db.StringProperty(required=True)
	desc =  db.TextProperty()
	rating = db.FloatProperty()
	fanart = db.StringProperty()
	genre = db.StringProperty()
	status = db.StringProperty(required=True, choices=set(["Ended", "Continuing", "On Hiatus", "Other"]))
	imdb_id = db.StringProperty(required=True)

