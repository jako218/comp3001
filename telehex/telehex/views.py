from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect

from google.appengine.api import users

from telehex.models import Greeting

import sys
sys.path.insert(0, 'libs')

from telehex.scraper import Scraper


import urllib

def index(request):
    template_values = {}
    return direct_to_template(request, 'telehex/index.html', template_values)

def search(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/')
    else:
        template_values =  {}
        return direct_to_template(request, 'telehex/search.html', template_values)

def scrape(request):
    return HttpResponseRedirect('/show/walking_dead')

def show(request, show_name):
    template_values = { 'show_name': show_name, }
    return direct_to_template(request, 'telehex/show.html', template_values)
