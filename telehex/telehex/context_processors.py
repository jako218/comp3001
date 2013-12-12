from google.appengine.api import users

def user_processor(request):
    return { 'user': users.get_current_user() }

def admin_processor(request):
    return { 'is_admin': users.is_current_user_admin() }
