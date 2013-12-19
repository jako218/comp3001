from google.appengine.ext import db
from django.shortcuts import render
from google.appengine.api import users
from google.appengine.api import mail
from models import User, TVShow
from datetime import date, timedelta

def email_update(request):
    
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
            episodes_query = db.GqlQuery("SELECT * FROM TVEpisode WHERE airdate >= :today AND airdate < :weektoday AND ANCESTOR IS :showid ORDER BY airdate", today = date.today(), weektoday = weektoday, showid = showid)
            
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

        
        mail.send_mail( sender="updates@telehex3001.appspotmail.com",
                        to="{0}".format(user.email),
                        subject="Telehex - Your weekly episode email",
                        body=message)

        messages_sent += 1

    return render(request, 'telehex/email_update.html', {"messages_sent" : messages_sent})