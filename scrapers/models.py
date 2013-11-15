#!/usr/bin/env python
"""
TV Episode Model
"""

from google.appengine.ext import db

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

