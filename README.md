# comp3001

To run the python scripts, you need to use `virtualenv`!

Run this in the root of the repo:

```
$ sudo apt-get install virtualenv *or* brew install virtualenv
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ python scrapers/seriesscraper.py
```

## Data

### Series

 - Title
 - Description
 - Rating
 - Fanart
 - Genre
 - Status
 - IMDB ID

### Episodes

 - Episode Name
 - Season it's in
 - Overview/description
 - Episode number
 - Thumbnail
 - Air date
 - Rating
 - IMDB ID
