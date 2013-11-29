from django.conf.urls.defaults import *
from telehex.views import *

urlpatterns = patterns('',
    (r'^$', index),
    (r'^search/$', search),
    (r'^scrape/([0-9]+)$', scrape),
    (r'^show/(\w+)$', show),
    (r'^profile/$', profile),
    (r'^login/$', login),
    (r'^logout/$', logout),
    (r'^subscribe/$', subscribe),
    (r'^unsubscribe/$', unsubscribe),
)
