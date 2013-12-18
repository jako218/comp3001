from django.conf.urls.defaults import *
from telehex.views import *
from telehex.tasks import email_update

urlpatterns = patterns('',
    (r'^$', index),
    (r'^admin/$', admin),
    (r'^admin/togglescraping/$', togglescraping),
    (r'^data/calendar/$', calendar_data),
    (r'^data/ratings/', ratings_data),
    (r'^data/similarity/', similarity_data),
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
