#!/usr/bin/env python
#coding: utf-8
"""
:mod:`ratings_helper` -- Ratings Display
=================================================

.. module:: ratings_helper
   :synopsis: Adds functionality to Django template -
    Displays the ratings icons on the profile page

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

from django import template
import math

register = template.Library()


@register.filter
def to_num_hex(rating):
    """
    Outputs a quantity of hexagons based on the rating passed in

    :param rating: The rating to be outputted
    """
    spans = ""
    solid_hex = int(math.floor(rating / 2))
    for i in range(solid_hex):
        spans += "⬣"

    return spans