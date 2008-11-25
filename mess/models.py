# -*- coding: utf-8 -*-

import urllib
import hashlib
import logging

from google.appengine.ext import db
from google.appengine.api import users

from appengine_django.models import BaseModel

from django.utils.html import escape
from django.http import HttpResponseRedirect

roles = {
    'Admin': -1,
    'সদস্য': 0,
    'ম্যানেজার': 1,
}

role_list = []
for key, value in roles.iteritems():
    if key is not 'Admin':
        role_list.append((value, key))

class Member(BaseModel):
    """ Member model """
    user = db.UserProperty()
    nick = db.StringProperty(verbose_name="নাম")
    email = db.EmailProperty(verbose_name="ইমেইল")
    role_id = db.IntegerProperty()
    active = db.BooleanProperty(default=True, verbose_name="সক্রিয়তা")

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
        return escape(gravatar_url)

    @staticmethod
    def role(role):
        def wrapper(handler_method):
            def check_login(self, *args, **kwargs):
                user = Member.current_user()
                if not user:
                    logging.info("User not logged in -- force login")
                    return HttpResponseRedirect(users.create_login_url('/member/'))
                elif role == 'member' or \
                    (role == 'manager' and user.role_id == roles['ম্যানেজার']) or \
                    (role == "admin" and users.is_current_user_admin()):
                        logging.info("Allowing role (%s) for (%s)" % (role, user.nick))
                        return handler_method(self, *args, **kwargs)
                else:
                    roles_rev = {}
                    for key, value in roles.iteritems():
                        roles_rev.update({value:key})
                    logging.info("Not allowed (%s:%s) on (%s)" % (user.nick, roles_rev[user.role_id], handler_method.__name__))
                    return HttpResponseRedirect('/member/')
            return check_login
        return wrapper

class Meal(BaseModel):
    breakfast = db.BooleanProperty(verbose_name="সকালের নাস্তা", required=False)
    lunch = db.BooleanProperty(verbose_name="দুপুরের খাবার", required=False)
    supper = db.BooleanProperty(verbose_name="রাতের খাবার", required=False)
    extra = db.FloatProperty(verbose_name="অতিরিক্ত", required=False)

    date = db.DateProperty()
    member = db.ReferenceProperty(Member, required=False)
