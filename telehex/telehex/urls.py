from django.conf.urls.defaults import *
from telehex.views import *

urlpatterns = patterns('',
    (r'^$', index),
    (r'^calendar_data/$', calendar_data),
    (r'^graph_data/(\w+)$', graph_data),
    (r'^hexagons/([0-9]+)$', hexagon),
    (r'^login/$', login),
    (r'^logout/$', logout),
    (r'^profile/$', profile),
    (r'^profile/calendar/$', calendar),
    (r'^scrape/([0-9]+)$', scrape),
    (r'^search/$', search),
    (r'^search_tags/$', search_tags),
    (r'^show/(\w+)$', show),
    (r'^stats/(\w+)$', stats),
    (r'^stats2/(\w+)$', stats2),
    (r'^subscribe/$', subscribe),
    (r'^get_show_children/([0-9]+)$', get_show_children),
    (r'^unsubscribe/$', unsubscribe),
)
