# COMP3001 - Telehex

We're using Google App Engine. To run the website, you'll need to have it
installed. You can download it
[here](https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python),
or use `brew install google-app-engine` if on a mac.

You'll also need to make sure you've got the correct python requirements
installed. You can do this by creating and using a virtual environment:

```
$ cd comp3001
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

You can then start up Google's App Engine and view the site on your own machine
by using the command:

```
$ dev_appserver.py --clear_datastore 'true' telehex
```

from the root of the repo. The `--clear_datastore 'true'` bit is optional - if
used, it'll just clear your datastore everytime you restart the server.

You can now access the site at [http://localhost:8080](http://localhost:8080) or access the Google control panel at [http://localhost:8000](http://localhost:8000)

## Pages on the site

| URL (relative)       | Name                       | Template        |
|----------------------|----------------------------|-----------------|
| `/`                  | Home/Search                | `index.html`    |
| `/admin`             | Admin Panel                | `admin.html`    |
| `/calendar_data`     | Calendar Data (for AJAX)   | *N/A*           |
| `/hexagons/12345`    | Hexagons                   | *N/A*           |
| `/login`             | Login                      | *N/A*           |
| `/logout`            | Logout                     | *N/A*           |
| `/profile/calendar`  | User Calendar              | `calendar.html` |
| `/profile`           | User Profile               | `profile.html`  |
| `/ratings/show_slug` | Ratings Graphs             | `ratings.html`  |
| `/ratings_data`      | Ratings Data (for AJAX)    | *N/A*           |
| `/scrape`            | Scrape                     | *N/A*           |
| `/search_tags`       | Offline Search Fallback    | *N/A*           |
| `/search`            | Search Results             | `search.html`   |
| `/show/show_slug`    | Show Info                  | `show.html`     |
| `/similar/show_slug` | Similarity Graph           | `similar.html`  |
| `/similarity_data`   | Similarity Data (for AJAX) | *N/A*           |
| `/stats/show_slug`   | Show Stats/Graphs          | `stats.html`    |
| `/subscribe`         | Subscribe                  | *N/A*           |
| `/togglescraping`    | Toggle Scraping            | *N/A*           |
| `/unsubscribe`       | Unsubscribe                | *N/A*           |
| *(Every Page)*       | Footer                     | `footer.html`   |
| *(Every Page)*       | Header                     | `header.html`   |
| *N/A*                | Show Not Found             | `notfound.html` |
