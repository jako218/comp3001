from django.conf.urls.defaults import *
from telehex.views import *

urlpatterns = patterns('',
    (r'^$', index),
    (r'^search/$', search),
    (r'^scrape/$', scrape),
    (r'^show/(\w+)$', show),
)
