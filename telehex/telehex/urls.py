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

from django.conf.urls.defaults import *
from telehex.views import *
from telehex.tasks import email_update
from django.template.loader import add_to_builtins

add_to_builtins('django.templatetags.static')

urlpatterns = patterns('',
                       (r'^$', index),
                       (r'^admin/$', admin),
                       (r'^admin/togglescraping/$', togglescraping),
                       (r'^data/calendar/$', calendar_data),
                       (r'^data/ratings/', ratings_data),
                       (r'^data/similarity/', similarity_data),
                       (r'^genre/(\w+)$', genre),
                       (r'^hexagons/([0-9]+)$', hexagon),
                       (r'^login/$', login),
                       (r'^logout/$', logout),
                       (r'^profile/$', profile),
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
                       (r'^unsubscribe/$', unsubscribe),
)
