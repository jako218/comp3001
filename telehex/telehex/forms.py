"""
:mod:`forms` - Django Forms
=================================================

.. module:: forms
   :synopsis: Creates forms for the site

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

from django import forms


class EditTVShowForm(forms.Form):
    """
    A Class used to create the form for editing a TV show
    """

    textFieldWidget = forms.TextInput(attrs={'class': 'form-control'})

    title = forms.CharField(label='Title:', widget=textFieldWidget)
    desc = forms.CharField(label='Description:', required=False,
                           widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}))
    rating = forms.FloatField(label="Rating:", required=False, widget=textFieldWidget)
    status = forms.ChoiceField(choices=(("Continuing", "Continuing"), ("Ended", "Ended"),
                                        ("On Hiatus", "On Hiatus"), ("Other", "Other")), label='Choice:', required=True,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    fanart = forms.URLField(label='Fanart:', required=False, widget=textFieldWidget)
    genre = forms.CharField(label='Genre:', required=False, widget=textFieldWidget)
    subgenre = forms.CharField(label='Sub-genre:', required=False, widget=textFieldWidget)
    imdb_id = forms.CharField(label='IMDB ID:', required=False, widget=textFieldWidget)
    num_seasons = forms.IntegerField(label='Number of Seasons:', required=True, widget=textFieldWidget)
    disable_scraping = forms.BooleanField(label="Disable All Scraping:", required=False)
    disable_ep_rating_scraping = forms.BooleanField(label="Disable Episode Rating Scraping:", required=False)
    disable_fanart_scraping = forms.BooleanField(label="Disable Fanart Scraping:", required=False)
    disable_tvshow_scraping = forms.BooleanField(label="Disable TVShow Scraping:", required=False)
    disable_tvepisode_scraping = forms.BooleanField(label="Disable TVEpisode Scraping:", required=False)
    disable_ep_desc_display = forms.BooleanField(label="Disable Episode Description Display:", required=False)
