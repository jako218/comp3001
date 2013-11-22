from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect

from google.appengine.ext import db
from google.appengine.api import users

import sys
sys.path.insert(0, 'libs')

from telehex.scraper import Scraper, Search


import urllib

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

def scrape(request):
    return HttpResponseRedirect('/show/walking_dead')

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
