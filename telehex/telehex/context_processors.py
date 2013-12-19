"""
:mod:`context_processors`
=========================

.. module:: context_processors
   :synopsis: Provides variables to Django Templates Globally

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

from google.appengine.api import users


def user_processor(request):
    """
    Provides the user variable across all Django templates

    :param request: A HttpRequest
    :return: The current user
    """
    return {'user': users.get_current_user()}


def admin_processor(request):
    """
    Provides the is_admin boolean across all Django templates

    :param request: A HttpRequest
    :return: True or False depending on whether the current user is an admin
    """
    return {'is_admin': users.is_current_user_admin()}
