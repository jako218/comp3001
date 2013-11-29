from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect

# Increase the timeout for the show
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)

from google.appengine.ext import db
from google.appengine.api import users

import sys
sys.path.insert(0, 'libs')

from telehex.scraper import Scraper, Search
from models import TVShow

from datetime import datetime, timedelta
import urllib

RESCRAPE_AFTER = 7

def index(request):
    template_values = {}
    return direct_to_template(request, 'telehex/index.html', template_values)

def search(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/')
    else:
        query = request.POST.get('query')
        
        template_values =  { 'results': Search().search_tvdb(query) }
        return direct_to_template(request, 'telehex/search.html', template_values)

def scrape(request, tvdb_id):
    q = TVShow.get_by_key_name(tvdb_id)

    if q and q.last_scraped < datetime.now() - timedelta(days=RESCRAPE_AFTER):
        url_slug = q.url_string
    else:
        s = Scraper(tvdb_id)
        url_slug = s.get_url_slug()

    return HttpResponseRedirect("/show/{0}".format(url_slug))

def show(request, show_name):
    q = db.GqlQuery("SELECT * FROM TVShow WHERE url_string = :1", show_name)

    show = q.run(limit=1)
    if q.count() > 0:
        show = show.next()
    else:
        return direct_to_template(request, 'telehex/notfound.html', { 'query': show_name })

    q = db.GqlQuery("SELECT * FROM TVEpisode WHERE ANCESTOR IS :1 ORDER BY season, ep_number", show)
    episodes = q.run()

    template_values = { 'show': show, 'episode_iterator': episodes }
    return direct_to_template(request, 'telehex/show.html', template_values)
