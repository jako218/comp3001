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

| URL (relative)          | Name                        | Template        |
|-------------------------|-----------------------------|-----------------|
| `/`                     | Home/Search                 | `index.html`    |
| `/admin`                | Admin Panel                 | `admin.html`    |
| `/admin/togglescraping` | Toggle Scraping On/Off      |                 |
| `/data/calendar`        | Calendar Data (for AJAX)    |                 |
| `/data/ratings`         | Ratings Data (for AJAX)     |                 |
| `/data/similarity`      | Similarity Data (for AJAX)  |                 |
| `/hexagons/12345`       | Hexagon Images (fanart)     |                 |
| `/login`                | Login                       |                 |
| `/logout`               | Logout                      |                 |
| `/profile`              | User Profile                | `profile.html`  |
| `/profile/calendar`     | User Calendar               | `calendar.html` |
| `/ratings/show_slug`    | Ratings Graphs              | `ratings.html`  |
| `/receive_updates`      | Toggle Users' Email Updates |                 |
| `/scrape`               | Scrape Show Data            |                 |
| `/search`               | Search Results              | `search.html`   |
| `/search_tags`          | Offline Search Fallback     |                 |
| `/show/show_slug`       | Show Info                   | `show.html`     |
| `/similar/show_slug`    | Similarity Graph            | `similar.html`  |
| `/subscribe`            | Subscribe to Show           |                 |
| `/tasks/email_update`   | Email Update Cron Job       |                 |
| `/unsubscribe`          | Unsubscribe from Show       |                 |
|                         | Footer                      | `footer.html`   |
|                         | Header                      | `header.html`   |
|                         | Show Not Found              | `notfound.html` |
