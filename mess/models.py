import urllib
import hashlib
import logging

from google.appengine.ext import db
from google.appengine.api import users

from django.utils.html import escape

roles = {
    'Admin': -1,
    'Member': 0,
    'Manager': 1,
}

role_list = []
for key, value in roles.iteritems():
    if key is not 'Admin':
        role_list.append((value, key))

class Member(db.Model):
    """ Member model """
    user = db.UserProperty()
    email = db.EmailProperty()
    nick = db.StringProperty()
    role_id = db.IntegerProperty()
    active = db.BooleanProperty(default=True)

    def __unicode__(self):
        return self.nick

    @staticmethod
    def current_user():
        user = users.get_current_user()
        return user and Member.all().filter('user', user).get() or None

    def gravatar(self, size=64):
        gravatar_url = "http://www.gravatar.com/avatar.php?"
        gravatar_url += urllib.urlencode({
            'gravatar_id': hashlib.md5(self.email).hexdigest(),
            'size':str(size)})
        return """<img src="%s" alt="gravatar" />""" % escape(gravatar_url)

    @staticmethod
    def role(role):
        def wrapper(handler_method):
            def check_login(self, *args, **kwargs):
                user = Member.current_user()
                if not user:
                    if self.request.method != 'GET':
                        logging.info("Not user - aborting")
                        self.error(403)
                    else:
                        logging.info("User not logged in -- force login")
                        self.redirect(users.create_login_url(self.request.uri))
                elif role == 'member' or \
                    (role == 'manager' and user.role_id == roles['Manager']) or \
                    (role == "admin" and users.is_current_user_admin()):
                        logging.info("Allowing role (%s) for (%s)" % (role, user.nick))
                        handler_method(self, *args, **kwargs)
                else:
                    roles_rev = {}
                    for key, value in roles.iteritems():
                        roles_rev.update({value:key})
                    logging.info("Not allowed (%s:%s) on (%s)" % (user.nick, roles_rev[user.role_id], handler_method.__name__))
                    if self.request.method != 'GET':
                        self.error(404)
                    else:
                        self.redirect('/')
            return check_login
        return wrapper

class Meal(db.Model):
    breakfast = db.BooleanProperty()
    lunch = db.BooleanProperty()
    supper = db.BooleanProperty()
    extra = db.FloatProperty()

    date = db.DateProperty()
    member = db.ReferenceProperty(Member)
