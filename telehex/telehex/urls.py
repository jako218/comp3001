from django.conf.urls.defaults import *
from telehex.views import *

urlpatterns = patterns('',
    (r'^$', index),
    (r'^admin/$', admin),
    (r'^calendar_data/$', calendar_data),
    (r'^show_children/', show_children),
    (r'^hexagons/([0-9]+)$', hexagon),
    (r'^login/$', login),
    (r'^logout/$', logout),
    (r'^profile/$', profile),
    (r'^profile/calendar/$', calendar),
    (r'^scrape/([0-9]+)$', scrape),
    (r'^search/$', search),
    (r'^search_tags/$', search_tags),
    (r'^show/(\w+)$', show),
    (r'^ratings/(\w+)$', ratings),
    (r'^ratings_data/', ratings_data),
    (r'^stats2/(\w+)$', stats2),
    (r'^subscribe/$', subscribe),
    (r'^togglescraping/$', togglescraping),
    (r'^unsubscribe/$', unsubscribe),
)
