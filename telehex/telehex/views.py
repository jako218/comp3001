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

def stats(request, show_title):
    q = db.GqlQuery("SELECT * FROM TVShow WHERE url_string = :1", show_title)

    show = q.run(limit=1)
    if q.count() > 0:
        show = show.next()
    else:
        return direct_to_template(request, 'telehex/notfound.html', { 'query': show_title })

    template_values =  { 'show' : show }
    return direct_to_template(request, 'telehex/stats.html', template_values)

def stats2(request, show_title):
    q = db.GqlQuery("SELECT * FROM TVShow WHERE url_string = :1", show_title)

    show = q.run(limit=1)
    if q.count() > 0:
        show = show.next()
    else:
        return direct_to_template(request, 'telehex/notfound.html', { 'query': show_title })

    q = db.GqlQuery("SELECT user_id from UserShow WHERE show_id = :id", id=int(show.key().name()))
    user_ids = [userid.user_id for userid in q.run()]

    q = db.GqlQuery("SELECT show_id from UserShow WHERE user_id IN :ids", ids=user_ids)
    show_ids = [showid.show_id for showid in q.run()]
    
    template_values =  {};
    return direct_to_template(request, 'telehex/stats2.html', template_values)

def graph_data(request, show_title):
    q = db.GqlQuery("SELECT * FROM TVShow WHERE url_string = :1", show_title)
    
    show = q.run(limit=1)
    if q.count() > 0:
        show = show.next()
    else:
        return HttpResponseRedirect('/')

    events = []

    q = db.GqlQuery("SELECT name, season, ep_number, rating FROM TVEpisode WHERE ANCESTOR IS :1 ORDER BY season, ep_number", show)
    episodes = q.run()

    seasons = {key: [] for key in range(1, show.num_seasons+1)}

    # Create dict of seasons with dicts of ep_num:rating 
    for e in episodes:
        seasons[e.season].append({'name': "{0}".format(e.name.encode('utf8')), 'episode':e.ep_number, 'rating':e.rating, 'url': "/show/{0}#s{1:02d}e{2:02d}".format(show.url_string, e.season, e.ep_number)}) 

    # Check for any empty seasons
    for key in seasons.keys():
        if len(seasons[key]) == 0:
            seasons.pop(key, None)

    return HttpResponse(json.dumps(seasons), content_type="application/json")
    return HttpResponseRedirect('/')

def scrape(request, tvdb_id):
    q = TVShow.get_by_key_name(tvdb_id)
    
    if users.is_current_user_admin() and 'force' in request.GET and request.GET['force'] == '1':
        s = Scraper(tvdb_id)
        return HttpResponseRedirect("/show/{0}".format(s.get_url_slug()))

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
        u = UserShow.get_by_key_name("{0}{1}".format(user.user_id(), show.key().name()))
        if u:
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

    template_values = { 'is_admin': users.is_current_user_admin(), 'show': show, 'seasons_dict': seasons, 'subscribed': subscribed, 'nextepisode': nextepisode }
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
        return HttpResponseRedirect('/login?continue={0}'.format(request.get_full_path()))

    q = db.GqlQuery("SELECT show_id FROM UserShow WHERE user_id = :id", id=user.user_id())
    show_ids = [str(showid.show_id) for showid in q.run()]

    template_values = { }

    # Get the subscribed TVShows based on the show id
    subscribed_tv_shows = TVShow.get_by_key_name(show_ids)

    subs_next_episodes = []
    for ids in subscribed_tv_shows:
        q = db.GqlQuery("SELECT * FROM TVEpisode WHERE airdate >= :1 AND ANCESTOR IS :2 ORDER BY airdate LIMIT 1", date.today(), ids)
        nextepisode = q.run()
        if q.count() > 0:
            subs_next_episodes.append(nextepisode.next())
        else:
            subs_next_episodes.append(None)

        template_values = { 'shows': sorted(zip(subscribed_tv_shows, subs_next_episodes), key=lambda x: x[1].airdate if x[1] else date(MAXYEAR, 12, 31)) }
    return direct_to_template(request, 'telehex/profile.html', template_values)

def login(request):
    user = users.get_current_user()
    if not user:
        if 'continue' in request.GET:
            return HttpResponseRedirect(users.create_login_url(request.GET['continue']))
        else:
            return HttpResponseRedirect(users.create_login_url('/'))

    return HttpResponseRedirect('/')

def logout(request):
    user = users.get_current_user()
    if user:
        if 'continue' in request.GET:
            return HttpResponseRedirect(users.create_logout_url(request.GET['continue']))
        else:
            return HttpResponseRedirect(users.create_logout_url('/'))

    return HttpResponseRedirect('/')

def subscribe(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.META['HTTP_REFERER']))

    if request.method != 'POST':
        return HttpResponseRedirect('/')

    tvdb_id = int(request.POST.get('show_id'))
    
    # Put a link from a show to a user
    UserShow(
        key_name="{0}{1}".format(user.user_id(), tvdb_id),
        user_id=user.user_id(),
        show_id=tvdb_id
    ).put()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unsubscribe(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.META['HTTP_REFERER']))

    if request.method != 'POST':
        return HttpResponseRedirect('/')

    tvdb_id = int(request.POST.get('show_id'))
    

    q = db.GqlQuery("SELECT * FROM UserShow WHERE user_id = :id AND show_id = :show", id=user.user_id(), show=tvdb_id)
    usershow = q.fetch(limit=1)[0]
    usershow.delete()

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

    q = db.GqlQuery("SELECT show_id FROM UserShow WHERE user_id = :id", id=user.user_id())
    show_ids = [str(showid.show_id) for showid in q.run()]

    subs_shows_entities = TVShow.get_by_key_name(show_ids)

    events = []
    for entity in subs_shows_entities:
        q = db.GqlQuery('SELECT * FROM TVEpisode WHERE airdate >= :start AND airdate <= :end AND ANCESTOR IS :ancestor', ancestor=entity, start=datetime.fromtimestamp(int(request.GET.get('start'))), end=datetime.fromtimestamp(int(request.GET.get('end'))))
        episode_iterator = q.run()

        for episode in episode_iterator:
            events.append({'title': "{0}\n{1}".format(entity.title, episode.name.encode('utf8')), 'start': episode.airdate.strftime('%Y-%m-%d'), 'url': "/show/{0}#s{1:02d}e{2:02d}".format(entity.url_string, episode.season, episode.ep_number)})

    return HttpResponse(json.dumps(events), content_type="application/json")

def admin(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue=/admin')

    q = db.GqlQuery("SELECT * FROM TVShow")
    show_iterator = q.run()

    q = db.GqlQuery("SELECT * FROM UserShow")
    subs_iterator = q.run()
    subs_counts = {}

    for sub in q.run():
        if str(sub.show_id) in subs_counts:
            subs_counts[str(sub.show_id)] += 1
        else:
            subs_counts[str(sub.show_id)] = 1

    print subs_counts

    template_values = { 'is_admin': users.is_current_user_admin(), 'show_iterator': show_iterator, 'subs_counts': subs_counts }

    return direct_to_template(request, 'telehex/admin.html', template_values)

