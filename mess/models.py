# -*- coding: utf-8 -*-

import urllib
import hashlib
import logging
import datetime

from google.appengine.ext import db
from google.appengine.api import users

from appengine_django.models import BaseModel

from django.utils.html import escape
from django.http import HttpResponseRedirect

roles = {
    'member': 0,
    'manager': 1,
}

class Member(BaseModel):
    """ Member model """
    user = db.UserProperty()
    nick = db.StringProperty(verbose_name="নাম")
    email = db.EmailProperty(verbose_name="ইমেইল")
    role_id = db.IntegerProperty(default=roles['member'])
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
                if users.is_current_user_admin():
                    logging.info("Allowing role (%s) for (%s)" % (role, users.get_current_user()))
                    logging.info("Since s/he is admin")
                    return handler_method(self, *args, **kwargs)

                user = Member.current_user()
                if not user:
                    logging.info("User not logged in -- force login")
                    return HttpResponseRedirect(users.create_login_url('/'))
                elif role == 'member' or \
                    (role == 'manager' and user.role_id == roles['manager']):
                        logging.info("Allowing role (%s) for (%s)" % (role, user.nick))
                        return handler_method(self, *args, **kwargs)
                else:
                    roles_rev = {}
                    for key, value in roles.iteritems():
                        roles_rev.update({value:key})
                    logging.info(u"Not allowed (%s) on (%s)" % (user.nick, handler_method.__name__))
                    return HttpResponseRedirect('/')
            return check_login
        return wrapper

    def get_meal(self, date):
        return self.meal_set.filter('date =', date).get()

class Meal(BaseModel):
    breakfast = db.BooleanProperty(verbose_name="সকালের নাস্তা", required=False)
    lunch = db.BooleanProperty(verbose_name="দুপুরের খাবার", required=False)
    supper = db.BooleanProperty(verbose_name="রাতের খাবার", required=False)
    extra = db.FloatProperty(verbose_name="অতিরিক্ত", required=False)

    date = db.DateProperty()
    member = db.ReferenceProperty(Member, required=False)

    @staticmethod
    def day_total(date):
        meals = Meal.all().filter('date =', date)
        total = {
            'breakfast': 0,
            'lunch': 0,
            'supper': 0,
            'extra': 0.0,
            'count': meals.count(),
        }
        if meals:
            for meal in meals:
                if meal.breakfast:
                    total['breakfast'] += 1
                if meal.lunch:
                    total['lunch'] += 1
                if meal.supper:
                    total['supper'] += 1
                total['extra'] += meal.extra

        total['total'] = total['breakfast']/2. + total['lunch'] + total['supper'] + total['extra']
        return total

    @staticmethod
    def month_total(month, year):
        month = int(month)
        year = int(year)
        start = datetime.date(year=year, month=month, day=1)
        month += 1
        if month > 12:
            month = 1
        end = datetime.date(year=year, month=month, day=1)

        meals = Meal.all().filter('date >=', start).filter('date <', end)
        total = {
            'member': {},
            'breakfast': 0,
            'lunch': 0,
            'supper': 0,
            'extra': 0.0,
        }
        if meals:
            for meal in meals:
                member_key = meal.member.key()
                if not total['member'].has_key(member_key):
                    total['member'][member_key] = {
                        'nick': meal.member.nick,
                        'breakfast': 0,
                        'lunch': 0,
                        'supper': 0,
                        'extra': 0.0,
                    }
                if meal.breakfast:
                    total['breakfast'] += 1
                    total['member'][member_key]['breakfast'] += 1
                if meal.lunch:
                    total['lunch'] += 1
                    total['member'][member_key]['lunch'] += 1
                if meal.supper:
                    total['supper'] += 1
                    total['member'][member_key]['supper'] += 1
                total['extra'] += meal.extra
                total['member'][member_key]['extra'] += meal.extra

        total['total'] = total['breakfast']/2. + total['lunch'] + total['supper'] + total['extra']
        total['count'] = len(total['member'])
        return total

