"""
:mod:`urls`
=================================================

.. module:: urls
   :synopsis: Adds the telehex urls pattern to Djangos urls

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""


#!/usr/bin/env python
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('telehex.urls')),
)
