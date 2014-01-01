"""
:mod:`urls` - Django URLS
=================================================

.. module:: urls
   :synopsis: Mappings between regular expressions and view. Used to determine which page to render give a specific URL

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

# Django Imports
from django.conf.urls.defaults import *
from django.template.loader import add_to_builtins

# Telehex Imports
from telehex.views import *
from telehex.tasks import email_update

add_to_builtins('django.templatetags.static')

# Specify the valid URL patterns for the site
urlpatterns = patterns('',
                       (r'^$', index),
                       (r'^admin/$', admin),
                       (r'^admin/edit_show/([0-9]+)$', edit_show),
                       (r'^admin/togglescraping/$', togglescraping),
                       (r'^data/calendar/$', calendar_data),
                       (r'^data/ratings/', ratings_data),
                       (r'^data/similarity/', similarity_data),
                       (r'^genre/(.*)$', genre),
                       (r'^hexagons/([0-9]+)$', hexagon),
                       (r'^login/$', login),
                       (r'^logout/$', logout),
                       (r'^profile/$', profile),
                       (r'^profile/stats/$', profile_stats),
                       (r'^profile/stats_data/$', profile_stats_data),
                       (r'^profile/stats_pie_genre/$', profile_stats_pie_genre),
                       (r'^profile/stats_pie_ratings/$', profile_stats_pie_ratings),
                       (r'^profile/stats_pie_status/$', profile_stats_pie_status),
                       (r'^profile/calendar/$', calendar),
                       (r'^ratings/(\w+)$', ratings),
                       (r'^receive_updates/$', receive_email_updates),
                       (r'^scrape/([0-9]+)$', scrape),
                       (r'^search/$', search),
                       (r'^search_tags/$', search_tags),
                       (r'^show/(\w+)$', show),
                       (r'^similar/(\w+)$', similar),
                       (r'^subscribe/$', subscribe),
                       (r'^tasks/email_update$', email_update),
                       (r'^unsubscribe/$', unsubscribe));
