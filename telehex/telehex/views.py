from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse

# Increase the timeout for the show
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)

from google.appengine.ext import db
from google.appengine.api import users

from collections import Counter

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

    template_values =  { "show" : show};
    return direct_to_template(request, 'telehex/stats2.html', template_values)

def graph_data(request, show_title):
    q = db.GqlQuery("SELECT * FROM TVShow WHERE url_string = :1", show_title)
    
    show = q.run(limit=1)
    if q.count() > 0:
        show = show.next()
    else:
        return HttpResponseRedirect('/')

    events = []

    q = db.GqlQuery("SELECT season, ep_number, rating FROM TVEpisode WHERE ANCESTOR IS :1 ORDER BY season, ep_number", show)
    episodes = q.run()

    seasons = {key: [] for key in range(1, show.num_seasons+1)}

    # Create dict of seasons with dicts of ep_num:rating 
    for e in episodes:
        seasons[e.season].append(e.rating) 

    # Check for any empty seasons
    for key in seasons.keys():
        if len(seasons[key]) == 0:
            seasons.pop(key, None)

    return HttpResponse(json.dumps(seasons), content_type="application/json")
    return HttpResponseRedirect('/')

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
        return HttpResponseRedirect(users.create_login_url(request.META['HTTP_REFERER']))
    else:
        return HttpResponseRedirect('/')

def logout(request):
    user = users.get_current_user()
    if user:
        return HttpResponseRedirect(users.create_logout_url(request.META['HTTP_REFERER']))
    else:
        return HttpResponseRedirect('/')

def subscribe(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login')

    if request.method != 'POST':
        return HttpResponseRedirect('/')

    tvdb_id = int(request.POST.get('show_id'))
    
    # Put a link from a show to a user
    UserShow(   key_name="{0}{1}".format(user.user_id(), tvdb_id),
                user_id=user.user_id(),
                show_id=tvdb_id
            ).put()



    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unsubscribe(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login')

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


def get_show_children(request, showid):
    # Get the show object for this stats page
    show = TVShow.get_by_key_name(showid)

    # Get all the user shows
    q = db.GqlQuery("SELECT user_id, show_id FROM UserShow")
    user_shows = [(sid.show_id, sid.user_id) for sid in q.run()]
    
    # Create a dictionary holding the show data
    show_json = generate_dict({"name": show.title, "showid" : "{0}".format(showid), "children": []}, showid, user_shows)
    # print json.dumps(show_json)

    return HttpResponse(json.dumps(show_json), content_type="application/json")

def generate_dict(d, showid,  user_shows, depth=3):
    # Base case
    if depth == 0:
        return None

    # Find all the user ids subscribed to this show
    user_ids =  [u[1] for u in user_shows if u[0] == int(showid)]

    # Find all the shows these users are subscribed to    
    show_ids = [s[0] for s in user_shows for u in user_ids if s[1] == u]

    # Get the top 7 shows
    top_7 =  Counter(show_ids).most_common(7)

    # Loop through the top 7 and get the ids
    top_7_ids = [str(i[0]) for i in top_7]
    
    # Remove your own show name from the list
    top_7_ids.remove(showid)
    
    # Get the show names
    tv_show_names = [t.title for t in TVShow.get_by_key_name(top_7_ids)]

    # Zip the shows so we can loop through them together
    tv_shows = zip(top_7_ids, tv_show_names)

    # For each show do the same thing!
    for x in tv_shows:
        children = generate_dict({"name": "{0}".format(x[1]), "showid" : "{0}".format(x[0]), "children": []}, x[0], user_shows, depth-1)
        if children:
            d['children'].append(children)
        else:
            if 'children' in d:
                d.pop('children')

    return d;

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