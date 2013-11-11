# comp3001

To run the python scripts, you need to use `virtualenv`! If you don't already
have `virtualenv` installed, you can install it with `pip install virtualenv`. 

Run this in the root of the repo:

```
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ python scrapers/seriesscraper.py `python scrapers/nametoid.py walking dead`
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
