from django.conf.urls.defaults import *
from telehex.views import *

urlpatterns = patterns('',
    (r'^$', index),
    (r'^hexagons/([0-9]+)$', hexagon),
    (r'^login/$', login),
    (r'^logout/$', logout),
    (r'^profile/$', profile),
    (r'^profile/calendar/$', calendar),
    (r'^scrape/([0-9]+)$', scrape),
    (r'^search/$', search),
    (r'^show/(\w+)$', show),
    (r'^subscribe/$', subscribe),
    (r'^unsubscribe/$', unsubscribe),
)
