#!/usr/bin/env python
"""
:mod:`apptags` -- Django template functions
=================================================

.. module:: apptags
   :synopsis: Adds the functionality of being able to access
   dictionary items withs keys in django templates

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Returns the value for a dictionary entry corresponding to key
    :param dictionary: The dictionary to be used
    :param key: The key of the dictionary to return the item from
    """

    return dictionary.get(key)
