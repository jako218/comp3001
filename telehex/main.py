import django.core.handlers.wsgi
import sys

sys.path.insert(0, 'libs') 
application = django.core.handlers.wsgi.WSGIHandler()
