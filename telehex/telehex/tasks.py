"""
:mod:`tasks` -- Cron job tasks
=================================================

.. module:: tasks
   :synopsis: Specifies the cron job tasks to be executed

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

# GAE Imports
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import users

# Django Imports
from django.shortcuts import render

# Telehex Imports
from models import TVShow

# Other Imports
from datetime import date, timedelta


def email_update(request):
    """
    A function which finds all the users who are subscribed to shows airing this week
    and for each user, generates an email with a list of these shows and when they're airing

    :param request: The request object for the page
    :return: A HttpResponse Object, which renders a page specifying how many emails were sent
    """

    # Get all the users
    q = db.GqlQuery("SELECT * FROM User")

    # Calculate 7 days from now to use in the query
    weektoday = date.today() + timedelta(days=7)

    messages_sent = 0
    for user in q.run():
        # For each user get the shows they're subscribed to
        show_query = db.GqlQuery("SELECT show_id FROM UserShow WHERE user_id = :id", id=user.key().name())
        show_ids = [str(show.show_id) for show in show_query.run()]

        # Don't send email if they're not subscribed to any shows
        if len(show_ids) == 0:
            continue

        shows = TVShow.get_by_key_name(show_ids)

        # For all the shows subscribed to - find the shows which have episodes airing this week
        episodes_this_week = {}
        for showid in shows:
            episodes_query = db.GqlQuery(
                "SELECT * FROM TVEpisode WHERE airdate >= :today AND airdate < :weektoday AND ANCESTOR IS :showid ORDER BY airdate",
                today=date.today(), weektoday=weektoday, showid=showid)

            # Create a list of all the episodes
            episodes = [episode for episode in episodes_query.run()]

            # Add a dictionary entry if episodes exist for a show
            if len(episodes) > 0:
                episodes_this_week[showid.title] = episodes

                # Don't send email if there are no episode airing this week
        if len(episodes_this_week) == 0:
            continue

        # Construct a message containing the episodes for this week
        message = "Hello Telehex Subscriber,\n\nThese are the shows you've subscribed to airing this week:\n\n"
        for key in sorted(episodes_this_week):
            message += "{0}:\n".format(key)
            for episode in episodes_this_week[key]:
                message += "\t{0} - {1}\n".format(episode.airdate.strftime("%B %d, %Y"), episode.name)
            message += "\n\n"

        # Get the server to send the mail
        mail.send_mail(sender="updates@telehex3001.appspotmail.com",
                       to="{0}".format(user.email),
                       subject="Telehex - Your weekly episode email",
                       body=message)

        messages_sent += 1

    # Task complete, return a response with the number of messages sent
    return render(request, 'telehex/email_update.html', {"messages_sent": messages_sent})
