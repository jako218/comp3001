from google.appengine.api import users

def user_processor(request):
    return { 'user': users.get_current_user() }
