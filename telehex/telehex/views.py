"""
:mod:`views` -- Generates the views for the site
================================================

.. module:: views
   :synopsis: Deals responses for requests issued by Django

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

# Django imports
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# GAE Imports
from google.appengine.ext import db
from google.appengine.api import users

# Telehex Imports
from models import *
from scraper import Scraper, Search

# Other Imports
from collections import Counter
from collections import OrderedDict
import csv
from datetime import datetime, timedelta, date, MAXYEAR
import json
from urllib import quote, unquote

# If a page is visited, this is the number of days which must have
# passed since the last scrape, before a re-scrape occurs
RESCRAPE_AFTER = 7

# The number of results to display per page
GENRE_RESULTS_PER_PAGE = 5
SEARCH_RESULTS_PER_PAGE = 10


def admin(request):
    """
    Returns the admin page HttpResponse if an admin user is logged in. If no user is logged in the user is redirected
    to the login page. If the user is logged in and not an admin they are redirected to a 404 page.

    :param request: The request object for this page.
    :returns: A HttpResponse Object
    :raises: Http404:
    """

    # Check if the current user is logged in
    if not users.get_current_user():
        return HttpResponseRedirect('/login?continue=/admin')

    # Check if the current user is an admin
    if not users.is_current_user_admin():
        raise Http404

    # Get all the TVShows
    q = db.GqlQuery("SELECT * FROM TVShow")
    show_iterator = q.run()

    # Get all the subscriptions
    q = db.GqlQuery("SELECT * FROM UserShow")
    subs_iterator = q.run()

    # Count the number of times a show has been subscribed to
    subs_counts = Counter([str(show.show_id) for show in subs_iterator])

    # Create a dictionary containing the variables required in the Django template
    template_values = {'show_iterator': show_iterator, 'subs_counts': subs_counts, 'is_scraping': settings.SCRAPING}
    return render(request, 'telehex/admin.html', template_values)


def calendar(request):
    """
    Deals with the calendar page requests. First checks if a user is logged in, if not, they're redirected to a login
    page, otherwise a response object is generated containing the calendar page

    :param request: The request object for this page.
    :return:  A HttpResponse Object
    """

    # Check if a user is logged in - if not redirect them to the login screen
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.get_full_path()))

    user_entry = User.get_by_key_name(user.user_id())

    return render(request, 'telehex/calendar.html', {"email_updates": user_entry})

def genre(request, genre_type):
    """
    Produces a list of all shows with the same genre ordered on the number of subscribed users it also checks the sub
    genre that are the same.

    :param request: A Genre request object.
    :param genre_type: The Genre to display all shows from
    :return: A HttpResponse Object containing the page of the genre requested.
    """

    # Decode the genre_type
    genre_type = unquote(genre_type)

    q = db.GqlQuery("SELECT * FROM TVShow WHERE genre = :genre", genre=genre_type)
    r1 = q.run()
    q = db.GqlQuery("SELECT * FROM TVShow WHERE subgenre = :genre", genre=genre_type)
    r2 = q.run()
    results_list = []

    # Get all the subscriptions
    q = db.GqlQuery("SELECT * FROM UserShow")
    subs_iterator = q.run()

    # Count the number of times a show has been subscribed to
    subs_counts = Counter([str(show.show_id) for show in subs_iterator])

    for r in r1:
        r.subscribed = subs_counts[str(r.key().name())]
        results_list.append(r)
    for r in r2:
        r.subscribed = subs_counts[str(r.key().name())]
        results_list.append(r)
    results_list.sort(key=lambda x: x.subscribed, reverse=True)
    paginator = Paginator(results_list, GENRE_RESULTS_PER_PAGE)

    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    template_values = {'results': results, 'genre': genre_type}
    return render(request, 'telehex/genre.html', template_values)

def index(request):
    """
    Return the index page of the site
    :param request: The request object for the index page. Used to generate the HttpResponse
    :return: A HttpResponse Object built from the `index.html` template.
    """
    return render(request, 'telehex/index.html')


def login(request):
    """
    Handles the logging in of users. If user is already logged in, they're redirected to the index of the site
    The actual logging in of users is handled by the Google App Engine (GAE)

    :param request: The request object for the login page.
    :return: A HttpResponseRedirect Object
    """

    # Ascertain whether a user is logged in, if not return the login screen, if they are, redirect to the index of site
    user = users.get_current_user()
    if not user:
        if 'continue' in request.GET:
            return HttpResponseRedirect(users.create_login_url(request.GET['continue']))
        else:
            return HttpResponseRedirect(users.create_login_url('/'))

    return HttpResponseRedirect('/')


def logout(request):
    """
    Handles the logging out of users. The actual logging out of a user is handle by the Google App Engine (GAE).

    :param request: The request object for the logout page.
    :return: A HttpResponseRedirect Object
    """

    user = users.get_current_user()
    if user:
        if 'continue' in request.GET:
            return HttpResponseRedirect(users.create_logout_url(request.GET['continue']))
        else:
            return HttpResponseRedirect(users.create_logout_url('/'))

    return HttpResponseRedirect('/')


def profile(request):
    """
    Returns the profile page for a specific user. The profile page allows a user to see which shows they have
    subscribed to and tells them how many days are left until a show airs.

    :param request: The request object for the profile page.
    :return: HttpResponse Object
    """

    # Check if a user is currently logged in - if not redirect to login screen
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.get_full_path()))

    # Retrieve all the show ids this user is subscribed to
    q = db.GqlQuery("SELECT show_id FROM UserShow WHERE user_id = :id", id=user.user_id())
    show_ids = [str(showid.show_id) for showid in q.run()]

    template_values = {}

    # Get the subscribed TVShows based on the show ids
    subscribed_tv_shows = TVShow.get_by_key_name(show_ids)

    # Determine the next episode yet to air. If all episodes have aired, get the latest aired episode
    subs_next_episodes = []
    for ids in subscribed_tv_shows:
        q = db.GqlQuery("SELECT * FROM TVEpisode WHERE airdate >= :1 AND ANCESTOR IS :2 ORDER BY airdate LIMIT 1",
                        date.today(), ids)
        nextepisode = q.run()
        if q.count() > 0:
            subs_next_episodes.append(nextepisode.next())
        else:
            subs_next_episodes.append(None)

        # Generate the template values. Have to zip the two lists so iteration is possible in Django. The shows list
        # is ordered based on closest episode of a continuing show. Ended shows latest episodes are given a max possible
        # date so that they appear at the end of the list
        template_values = {'shows': sorted(zip(subscribed_tv_shows, subs_next_episodes),
                                           key=lambda x: x[1].airdate if x[1] else date(MAXYEAR, 12, 31))}

    return render(request, 'telehex/profile.html', template_values)



def profile_stats(request):
    """
    Displays the profile stats page if a user is logged in and has subscribe to some shows

    :param request: The HTTP request for this page.
    :return: A HttpResponse Object containing the profile stats for this user
    """

    # Check if the user is logged in - if not redirect them to login
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.get_full_path()))
    
    q = db.GqlQuery("SELECT * FROM UserShow WHERE user_id=:id", id=user.user_id())
    q.run()

    # If a user has no shows they shouldn't be able to view this page, redirect back to their profile page
    if q.count() == 0:
        return render(request, 'telehex/profile.html')        

    return render(request, 'telehex/profile_stats.html')


def scrape(request, tvdb_id):
    """
    Takes a scrape request, constructs a Scraper object and performs a scrape for the show if it hasn't been scraped
    before or hasn't been scraped within the last :math:`x` days (where :math:`x` is the number of days specified by
    RESCRAPE_AFTER). Otherwise if the show exists and has been scraped within the last :math:`x` days redirect to the
    appropriate show page

    :param request: A Scrape request object.
    :param tvdb_id: The id of the tv show to be scraped (or shown)
    :return: A HttpResponse Object containing the page of the show requested.
    """

    # Determine if the show already exists in the datastore
    q = TVShow.get_by_key_name(tvdb_id)

    if users.is_current_user_admin() and 'force' in request.GET and request.GET['force'] == '1':
        s = Scraper(tvdb_id)
        return HttpResponseRedirect("/show/{0}".format(s.get_url_slug()))

    # Check if the show has been scraped before and if that scrape was in the last x days specified by RESCRAPE_AFTER
    if q and q.last_scraped > datetime.now() - timedelta(days=RESCRAPE_AFTER):
        url_slug = q.url_string
    else:
        # If scraping is switched on then scrape the show
        if settings.SCRAPING:
            s = Scraper(tvdb_id)
            url_slug = s.get_url_slug()
        else:
            url_slug = tvdb_id

    return HttpResponseRedirect("/show/{0}".format(url_slug))


def search(request):
    """
    Performs a search for a given string. A page with appropriate search results is returned

    :param request: A Search HttpRequest Object
    :return: A HttpResponse Object
    """

    # Check if this request has POST data - if not redirect to the home page, otherwise get the query
    if request.method == 'POST':
        search_string = request.POST.get('query')
        page_num = 1
    elif request.method == 'GET':
        search_string = request.GET.get('query')
        page_num = request.GET.get('p')

    # Get the results from this query
    results = Search().search_tvdb(search_string) if search_string else []

    # If one result go straight to the show page
    if len(results) == 1:
        return scrape(request, results[0]['tvdb_id'])

    paginator = Paginator(results, SEARCH_RESULTS_PER_PAGE)

    try:
        results = paginator.page(page_num)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    template_values = {'results': results, 'query': search_string }
    return render(request, 'telehex/search.html', template_values)


def show(request, show_title):
    """
    Takes a show title and construct a HttpResponse which contains the information for a specific show. The information
    include the show rating, the episodes in the show and whether or not the show is continuing.

    :param request: The HttpRequest object for the show page
    :param show_title: The title of the show in url string form, e.g. Breaking Bad would be breaking_bad
    :return: A HttpResponse Object
    """

    # Get the show based on the show_title
    show = get_tv_show(show_title)
    if not show:
        raise Http404

    # Determine if the user is subscribed
    user = users.get_current_user()
    is_user_sub = UserShow.get_by_key_name("{0}{1}".format(user.user_id(), show.key().name())) if user else None
    subscribed = True if is_user_sub else False

    # Select all the episodes for show        
    q = db.GqlQuery("SELECT * FROM TVEpisode WHERE ANCESTOR IS :1 ORDER BY season, ep_number", show)
    episodes = q.run()

    # Get the next airing episode if it exists
    q = db.GqlQuery("SELECT * FROM TVEpisode WHERE airdate >= :1 AND ANCESTOR IS :2 ORDER BY airdate LIMIT 1",
                    date.today(), show)
    nextepisode = q.run()
    nextepisode = nextepisode.next() if q.count() > 0 else None

    # Build a dictionary of season to episodes mappings
    seasons = {key: [] for key in range(1, show.num_seasons + 1)}
    for e in episodes:
        seasons[e.season].append(e)

    # Remove any seasons which have no episodes
    remove_empty_seasons(seasons)

    # Construct the recently viewed list - achieved by looking at the past shows visited which is stored in the cookie
    viewed_list = []
    if 'telehex_viewed' in request.COOKIES:
        viewed_list = json.loads(request.COOKIES['telehex_viewed'])

    viewed_list = [d for d in viewed_list if d['title'] != show.title]
    viewed_list.insert(0, {'title': show.title, 'url_string': show.url_string})

    show_genre = quote(show.genre) if show.genre else None
    show_subgenre = quote(show.subgenre) if show.subgenre else None

    template_values = {'show': show, 'seasons_dict': seasons, 'subscribed': subscribed, 'nextepisode': nextepisode,
                       'viewed_shows': viewed_list[:11], 'genre': show_genre, 'subgenre': show_subgenre}

    response = render(request, 'telehex/show.html', template_values)

    # Set the cookie of this response
    response.set_cookie('telehex_viewed', json.dumps(viewed_list[:11]))

    return response


def ratings(request, show_title):
    """
    Takes a show title and returns a page which contains graphs of all the episode rating

    :param request: A HttpRequest Object
    :param show_title: The title of the show in url string form, e.g. Breaking Bad would be breaking_bad
    :return: A HttpResponse Object
    """

    # Get the show based on the show_title
    show = get_tv_show(show_title)
    if not show:
        raise Http404

    # Pass show variable to template and redirect
    return render(request, 'telehex/ratings.html', {'show': show})


def similar(request, show_title):
    """
    Takes a show title and generates a page with a graph which identifies similar shows. This is based on which shows
    other users have subscribed to if they have also subscribed to this show

    :param request: The HttpRequest for the similar show page
    :param show_title: The title of the show in url string form, e.g. Breaking Bad would be breaking_bad
    :return: A HttpResponse Object
    """

    # Get the show based on the show_title
    show = get_tv_show(show_title)
    if not show:
        raise Http404

    # Pass show variable to template and redirect
    return render(request, 'telehex/similar.html', {'show': show})


def subscribe(request):
    """
    Subscribes the currently logged in user to the show specified in the request

    :param request: HttpRequest for subscribe
    :return: A HttpResponseRedirect object
    """

    # Determine if the user is logged in, if not redirect to login screen
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.META['HTTP_REFERER']))

    if request.method != 'POST':
        return HttpResponseRedirect('/')

    tvdb_id = int(request.POST.get('show_id'))

    # Add a subscription - a one-to-one mapping from show to user
    UserShow(
        key_name="{0}{1}".format(user.user_id(), tvdb_id),
        user_id=user.user_id(),
        show_id=tvdb_id
    ).put()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def togglescraping(request):
    """
    Takes a request from an admin user to switch scraping on and off across the site

    :param request: A HttpRequest object
    :return: A HttpResponseRedirect
    """

    if users.is_current_user_admin():
        settings.SCRAPING = not settings.SCRAPING

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def unsubscribe(request):
    """
    Unsubscribes the currently logged in user from the show specified in the request

    :param request: HttpRequest for subscribe
    :return: A HttpResponseRedirect object
    """

    # Determine if a user is logged in - if not redirect them to the login screen
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.META['HTTP_REFERER']))

    if request.method != 'POST':
        return HttpResponseRedirect('/')

    tvdb_id = int(request.POST.get('show_id'))

    # Remove the mapping between this user and the show from the UserShow table
    q = db.GqlQuery("SELECT * FROM UserShow WHERE user_id = :id AND show_id = :show", id=user.user_id(), show=tvdb_id)
    usershow = q.fetch(limit=1)[0]
    usershow.delete()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

########## FUNCTIONS ##########

def generate_dict(tree, showid, visited, user_shows, depth=4):
    """
    A recursive function to build the similar shows tree. By default the tree can go to a depth of 4. Initially the
    function is given a showid of a show. It then works by finding all the other shows users have subscribed to who
    have also subscribed to this show. It then takes the top 6 of these shows (based on number of subscribers),
    increments the depth and performs this function on each of these shows until a depth of 4 is reached and a similarity
    tree is built.

    :param tree: The tree dictionary at the current iteration of the recursion
    :param showid: The showid to find subtrees of and append to the tree dictionary
    :param visited: A list of the nodes already visited so they don't appear in the tree multiple times
    :param user_shows: A list of all the subscriptions
    :param depth: The depth the recursion should go to
    :return: A list containing the tree dictionary and a list of the nodes visited so far
    """

    # Base case, return a null list and the visited list
    if depth == 0:
        return [None, visited]

    # Find all the user ids subscribed to this show
    user_ids = [u[1] for u in user_shows if u[0] == int(showid)]

    # Find all the shows these users are subscribed to    
    show_ids = [s[0] for s in user_shows for u in user_ids if s[1] == u]

    # Remove any shows ids which have already appeared in the graph
    top_shows = [x for x in show_ids if str(x) not in visited]

    # Count each of the shows and get the most common
    show_count = Counter(top_shows).most_common()

    # Loop through and get the top 6 most popular show
    top_shows = [str(i[0]) for i in show_count[:6]]

    # Add the shows to the visited list
    visited.extend(top_shows)

    # Get the TV show entities from the database
    tv_shows = TVShow.get_by_key_name(top_shows)

    if len(tv_shows) == 0 and 'children' in tree:
        tree.pop('children')

    # For each show do the same thing!
    for show in tv_shows:
        showid = str(show.key().name())
        imagelink = "/hexagons/{0}".format(showid) if show.fanart else '/static/img/errorhex.png'
        [children, visited] = generate_dict(
            {"name": "{0}".format(show.title), "url": show.url_string, "showid": showid, "imagelink": imagelink,
             "children": []}, showid, visited, user_shows, depth - 1)

        # Check that children were returned, don't want to append an empty list to the tree
        if children:
            tree['children'].append(children)
        else:
            if 'children' in tree:
                tree.pop('children')

    return [tree, visited]


def get_tv_show(show_title):
    """
    A function which queries the datastore for a TVShow entity.

    :param show_title: The url_string of the show to be returned, e.g. Breaking Bad would be breaking_bad
    :return: TVShow Entity
    """

    # Try get a TVShow entity from the database based on the show_title
    q = db.GqlQuery("SELECT * FROM TVShow WHERE url_string = :1", show_title)
    show = q.run(limit=1)

    # Check if show exists - if it does return the show, else None
    tv_show = show.next() if q.count() > 0 else None
    return tv_show


def remove_empty_seasons(seasons):
    """
    A function which loops through a dictionary containing season-to-episodes mappings and removes any seasons which
    have no episodes in them

    :param seasons: A dictionary containing Season to Episode mappings
    :return: A dictionary with all the empty seasons removed
    """

    # Loop through the seasons keys and remove any which have a value of 0
    for key in seasons.keys():
        if len(seasons[key]) == 0:
            seasons.pop(key, None)
    return seasons

############ JSON & CSV #############

def calendar_data(request):
    """
    A function which returns the JSON required to construct a user's calendar

    :param request: A HttpRequest object
    :return: A HttpResponse containing the JSON for the similarity graph
    """

    # Check if the user is logged in - if not redirect them to the home page
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/')

    # Get all the showids of the shows a user is subscribed to
    q = db.GqlQuery("SELECT show_id FROM UserShow WHERE user_id = :id", id=user.user_id())
    show_ids = [str(showid.show_id) for showid in q.run()]

    # Get all the show entities corresponding to the show ids
    subs_shows_entities = TVShow.get_by_key_name(show_ids)

    # Obtains all the events for the date range specified in the url of the request
    events = []
    for entity in subs_shows_entities:
        q = db.GqlQuery("SELECT * FROM TVEpisode WHERE airdate >= :start AND airdate <= :end AND ANCESTOR IS :ancestor",
                        ancestor=entity, start=datetime.fromtimestamp(int(request.GET.get('start'))),
                        end=datetime.fromtimestamp(int(request.GET.get('end'))))
        episode_iterator = q.run()

        # For each episode in the date range, append to the events list
        for episode in episode_iterator:
            events.append({'title': "{0}\n{1}".format(entity.title, episode.name.encode('utf8')),
                           'start': episode.airdate.strftime('%Y-%m-%d'),
                           'url': "/show/{0}#s{1:02d}e{2:02d}".format(entity.url_string, episode.season,
                                                                      episode.ep_number)})

    # Return a JSON response containing all the shows for this date range
    return HttpResponse(json.dumps(events), content_type="application/json")

def create_profile_pie_data(request, attribute):
    """
    A function which generates a CSV response object for the pie charts on the user stats page 
    based on the show attribute passed in.

    :param request: A HttpRequest object
    :return: A HttpResponse containing the CSV for the pie chart
    """

    # Check if the user is logged in - if not redirect them to login
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.get_full_path()))

    # Get all the showids of the shows a user is subscribed to
    q = db.GqlQuery("SELECT show_id FROM UserShow WHERE user_id = :id", id=user.user_id())
    show_ids = [str(showid.show_id) for showid in q.run()]
    subs_shows_entities = TVShow.get_by_key_name(show_ids)

    # Count the number of occurences of each attribute
    counter_dict = Counter([getattr(show, attribute) for show in subs_shows_entities])

    # Generate the csv file
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow([attribute, 'Size'])
    for k, v in counter_dict.items():
        writer.writerow([k, v])

    # Return the response containing the csv data
    return response

def profile_stats_data(request):
    """
    A function which returns the JSON required to construct a user's stats page

    :param request: A HttpRequest object
    :return: A HttpResponse containing the JSON for the tree map
    """

    # Check if the user is logged in - if not redirect them to login
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/login?continue={0}'.format(request.get_full_path()))

    # Get all the showids of the shows a user is subscribed to
    q = db.GqlQuery("SELECT show_id FROM UserShow WHERE user_id = :id", id=user.user_id())
    show_ids = [str(showid.show_id) for showid in q.run()]

    # Get all the show entities corresponding to the show ids
    subs_shows_entities = TVShow.get_by_key_name(show_ids)

    show_children = []
    for show in subs_shows_entities:
        season_children = []

        # Get all the TVEpisodes for a show
        q = db.GqlQuery("SELECT * FROM TVEpisode WHERE ANCESTOR IS :ancestor ORDER BY season, ep_number", ancestor=show)
        episode_iterator = q.run()
        number_episodes = q.count()

        # Create a dictionary to hold the seasons - keyed by season number
        seasons = {key: [] for key in range(1, show.num_seasons + 1)}

        # For each episode, add it to the dictionary entry for it's corresponding season
        for episode in episode_iterator:
            if episode.rating > 0:
                seasons[episode.season].append({"name" : episode.name,
                                                "rating" : episode.rating,
                                                "url_string" : "/show/{0}#s{1:02d}e{2:02d}".format(show.url_string, 
                                                    episode.season, episode.ep_number)})
            else:
                seasons[episode.season].append({"name" : episode.name,
                                                "rating" : 0,
                                                "url_string" : "/show/{0}#s{1:02d}e{2:02d}".format(show.url_string, 
                                                    episode.season, episode.ep_number)})
        
        # Calculate the rating based on how many episodes are in the season
        for season in seasons:
            for episodes in seasons[season]:
                episodes['rating'] = episodes['rating'] / (number_episodes * len(seasons[season]))
            # Append each episode the the season list 
            season_children.append({"name" : season , "children" :  seasons[season] })

        # Append the show to the show list
        show_children.append({"name" : show.title, "children" : season_children})

    # Add the root name
    jsonEvents = {"name" : "Your shows" , "children" : show_children}

    return HttpResponse(json.dumps(jsonEvents), content_type="application/json")


def profile_stats_pie_genre(request):
    """
    A function which returns a CSV required to construct a pie chart on user's stats page

    :param request: A HttpRequest object
    :return: A HttpResponse containing the JSON for the tree map
    """
    return create_profile_pie_data(request, "genre")

def profile_stats_pie_ratings(request):
    """
    A function which returns a CSV required to construct a ratings pie chart on user's stats page

    :param request: A HttpRequest object
    :return: A HttpResponse containing the CSV for the ratings pie chart
    """
    return create_profile_pie_data(request, "rating")


def profile_stats_pie_status(request):
    """
    A function which returns a CSV required to construct a pie chart on user's stats page

    :param request: A HttpRequest object
    :return: A HttpResponse containing the JSON for the tree map
    """
    return create_profile_pie_data(request, "status")


def similarity_data(request):
    """
    A function which returns the JSON required to construct the show similarity graph

    :param request: A HttpRequest object
    :return: A HttpResponse containing the JSON for the similarity graph
    """

    if (request.method != 'POST'):
        return HttpResponseRedirect('/')

    # Get show title out of POST data
    showid = request.POST.__getitem__("show_id")

    # Get the show object for this stats page
    show = TVShow.get_by_key_name(showid)

    # Get all the user shows
    q = db.GqlQuery("SELECT user_id, show_id FROM UserShow")
    user_shows = [(sid.show_id, sid.user_id) for sid in q.run()]

    imagelink = "/hexagons/{0}".format(showid) if show.fanart else '/static/img/errorhex.png'
    # Create a dictionary holding the show data
    [show_json, visited] = generate_dict(
        {"name": show.title, "url": show.url_string, "showid": "{0}".format(showid), "imagelink": imagelink,
         "children": []}, showid, [str(showid)], user_shows)

    # It is possible that this show has no links
    if 'children' not in show_json:
        show_json['children'] = []

    return HttpResponse(json.dumps(show_json), content_type="application/json")


def ratings_data(request):
    """
    A function which returns the JSON required to construct the rating graphs

    :param request: A HttpRequest object
    :return: A HttpResponse containing the JSON for the rating graphs
    """

    if (request.method != 'POST'):
        return HttpResponseRedirect('/')

    # Get show title out of POST data
    show_title = request.POST.__getitem__("show_slug")

    # Get the show based on the show_title
    show = get_tv_show(show_title)

    if not show:
        # Show doesn't exist so redirect to index
        return HttpResponseRedirect('/')

    seasons = {key: [] for key in range(1, show.num_seasons + 1)}

    # Get the episode data for this show
    episodes = db.GqlQuery("SELECT name, season, ep_number, rating FROM TVEpisode WHERE ANCESTOR IS :1 ORDER BY season, "
                           "ep_number", show)

    # Create dict of seasons with dicts of ep_num:rating 
    for e in episodes.run():
        seasons[e.season].append(
            {'name': "{0}".format(e.name.encode('utf8')), 'episode': e.ep_number, 'rating': e.rating,
             'url': "/show/{0}#s{1:02d}e{2:02d}".format(show.url_string, e.season, e.ep_number)})

        # Remove any empty seasons
    remove_empty_seasons(seasons)

    no_ratings = []

    # Check for seasons with no ratings
    for key in seasons.keys():
        ratings = 'false'
        for ep in seasons[key]:
            if ep["rating"] >= 0:
                ratings = 'true'
        if ratings == 'false':
            no_ratings.append(key)

    data = {"shows": seasons, "no_ratings": no_ratings}

    return HttpResponse(json.dumps(data), content_type="application/json")


def search_tags(request):
    """
    A function which returns the JSON required for the auto-completing search

    :param request: A HttpRequest object
    :return: A HttpResponse containing the JSON of the tags required for the auto-complete search
    """
    q = db.GqlQuery('SELECT title FROM TVShow')
    show_names = [s.title for s in q.run()]
    return HttpResponse(json.dumps(dict(tags=show_names)), content_type="application/json")


########## OTHER ##########

def hexagon(request, show_id):
    """
    Retrieves the hexagon image for a particular show from the datastore

    :param request: A HttpRequest Object
    :param show_id: The show id for the hexagon wishing to be retrieved
    :return: A HttpResponse object containing the hexagon png
    """

    # Get the image relating to this show from the database
    q = TVShow.get_by_key_name(show_id)
    if q is None:
        return None

    hex_blob = HexImages.get_by_key_name(show_id, parent=q.key())

    # Covert the blob to a png and return in the response
    response = HttpResponse(mimetype="image/png")
    response.write(hex_blob.image)
    return response


def receive_email_updates(request):
    """
    A function used to set whether of not a user will receive weekly email updates

    :param request: A HttpRequest Object
    :return: A HttpResponse specifying whether or not the subscription to email updates failed or not
    """

    # Check a logged in user has issued this request
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/')

    user_entry = User.get_by_key_name(user.user_id())

    # If user already exists remove their email from table - otherwise add their email
    if user_entry:
        user_entry.delete()
        return HttpResponse(False)
    else:
        User(key_name=user.user_id(), email=user.email()).put()
        return HttpResponse(True)
