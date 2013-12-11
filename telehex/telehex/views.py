from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse

# Increase the timeout for the show
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)

from google.appengine.ext import db
from google.appengine.api import users

import sys
sys.path.insert(0, 'libs')

import json

from telehex.scraper import Scraper, Search
from models import *

from datetime import datetime, timedelta, date, MAXYEAR
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

    if q and q.last_scraped > datetime.now() - timedelta(days=RESCRAPE_AFTER):
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
        return direct_to_template(request, 'telehex/notfound.html', { 'query': show_name } )

    subscribed = False

    user = users.get_current_user()
    if user:
        u = UserSubscriptions.get_by_key_name(user.user_id())
        if u:
            if long(show.key().name()) in u.shows:
                subscribed = True

    q = db.GqlQuery("SELECT * FROM TVEpisode WHERE ANCESTOR IS :1 ORDER BY season, ep_number", show)
    episodes = q.run()

    q = db.GqlQuery("SELECT * FROM TVEpisode WHERE airdate >= :1 AND ANCESTOR IS :2 ORDER BY airdate LIMIT 1", date.today(), show)
    nextepisode = q.run()
    nextepisode = nextepisode.next() if q.count() > 0 else None

    seasons = {key: [] for key in range(1, show.num_seasons+1)}

    for e in episodes:
        seasons[e.season].append(e) 

    # Check for any empty seasons
    for key in seasons.keys():
        if len(seasons[key]) == 0:
            seasons.pop(key, None)

    template_values = { 'show': show, 'seasons_dict': seasons, 'subscribed': subscribed, 'nextepisode': nextepisode }
    return direct_to_template(request, 'telehex/show.html', template_values)

def hexagon(request, tvdb_id):
    q = TVShow.get_by_key_name(tvdb_id)
    img = HexImages.get_by_key_name(tvdb_id, parent=q.key())
    
    response = HttpResponse(mimetype="image/png")
    response.write(img.image)

    return response

def profile(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect(users.create_login_url(request.get_full_path()))

    template_values = { }
    subs_ids = UserSubscriptions.get_by_key_name(user.user_id())
    if subs_ids:
        subs_strings = [str(ids) for ids in subs_ids.shows]

        subs_shows_names = TVShow.get_by_key_name(subs_strings)

        subs_next_episodes = []
        for ids in subs_shows_names:
            q = db.GqlQuery("SELECT * FROM TVEpisode WHERE airdate >= :1 AND ANCESTOR IS :2 ORDER BY airdate LIMIT 1", date.today(), ids)
            nextepisode = q.run()
            if q.count() > 0:
                subs_next_episodes.append(nextepisode.next())
            else:
                subs_next_episodes.append(None)

        template_values = { 'shows': sorted(zip(subs_shows_names, subs_next_episodes), key=lambda x: x[1].airdate if x[1] else date(MAXYEAR, 12, 31)) }
    return direct_to_template(request, 'telehex/profile.html', template_values)

def login(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect(users.create_login_url(request.get_full_path()))
    else:
        return HttpResponseRedirect('/')

def logout(request):
    user = users.get_current_user()
    if user:
        return HttpResponseRedirect(users.create_logout_url(request.get_full_path()))
    else:
        return HttpResponseRedirect('/')

def subscribe(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login')

    if request.method != 'POST':
        return HttpResponseRedirect('/')

    tvdb_id = int(request.POST.get('show_id'))
    subs_shows = []

    u = UserSubscriptions.get_by_key_name(user.user_id())
    if u:
        subs_shows = u.shows
    
    if tvdb_id not in subs_shows:
        subs_shows.append(tvdb_id)

    UserSubscriptions(
            key_name = user.user_id(), 
            shows = subs_shows,
    ).put()
    
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unsubscribe(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login')

    if request.method != 'POST':
        return HttpResponseRedirect('/')

    tvdb_id = int(request.POST.get('show_id'))
    subs_shows = []

    u = UserSubscriptions.get_by_key_name(user.user_id())
    if u:
        subs_shows = u.shows

    if tvdb_id in subs_shows:
        subs_shows.remove(tvdb_id)

    UserSubscriptions(
            key_name = user.user_id(),
            shows = subs_shows
    ).put()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def calendar(request):
    return direct_to_template(request, 'telehex/calendar.html', { })

# JSON returns

def search_tags(request):
    q = db.GqlQuery('SELECT title FROM TVShow')
    show_names = [s.title for s in q.run()]
    return HttpResponse(json.dumps(dict(tags=show_names)), content_type="application/json")

def calendar_data(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/')

    u = UserSubscriptions.get_by_key_name(user.user_id())
    if u:
        subs_shows = u.shows

    subs_shows_strings = [str(ids) for ids in subs_shows]
    subs_shows_entities = TVShow.get_by_key_name(subs_shows_strings)

    events = []

    for entity in subs_shows_entities:
        q = db.GqlQuery('SELECT * FROM TVEpisode WHERE airdate >= :start AND airdate <= :end AND ANCESTOR IS :ancestor', ancestor=entity, start=datetime.fromtimestamp(int(request.GET.get('start'))), end=datetime.fromtimestamp(int(request.GET.get('end'))))
        episode_iterator = q.run()

        for episode in episode_iterator:
            events.append({'title': entity.title + " - " + episode.name, 'start': episode.airdate.strftime('%Y-%m-%d')})

    print json.dumps(dict(events=events))
    return HttpResponse(json.dumps(events), content_type="application/json")
    return HttpResponseRedirect('/')
