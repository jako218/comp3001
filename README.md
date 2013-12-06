# comp3001

We're using Google App Engine. To run the website, you'll need to have it
installed. You can download it
[here](https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python),
or use `brew install google-app-engine` if on a mac.

You'll also need to make sure you've got the correct python requirements
installed. You can do this by created and using a virtual environment:

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

| Name           | URL (relative)      | Template        |
|----------------|---------------------|-----------------|
| Home/Search    | `/`                 | `index.html`    |
| Search Results | `/search`           | `search.html`   |
| Show Info      | `/show/show_slug`   | `show.html`     |
| User Profile   | `/profile`          | `profile.html`  |
| User Calendar  | `/profile/calendar` | `calendar.html` |
| Show Not Found | *N/A*               | `notfound.html` |
| Header         | *(Every Page)*      | `header.html`   |
| Footer         | *(Every Page)*      | `footer.html`   |
| Login          | `/login`            | *N/A*           |
| Logout         | `/logout`           | *N/A*           |
| Subscribe      | `/subscribe`        | *N/A*           |
| Unsubscribe    | `/unsubscribe`      | *N/A*           |
| Scrape         | `/scrape`           | *N/A*           |
| Hexagons       | `/hexagons/12345`   | *N/A*           |

## Todo

* Stop breaking on null searches, do something when nothing matches search
* Make results page better
* Javascript calendar showing past/future episodes for user
* Javascript countdown on episode page
* Sort out CSS for most pages
* A whole bunch of Javascript graphs and data visualisations
* Refactor/tidy up most of the python code
* Make more backgrounds for main page
