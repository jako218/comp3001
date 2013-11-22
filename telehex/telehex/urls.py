from django.conf.urls.defaults import *
from telehex.views import main_page, sign_post, scrape

urlpatterns = patterns('',
    (r'^sign/$', sign_post),
    (r'^scrape/$', scrape),
    (r'^$', main_page),
)
