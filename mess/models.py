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

class Mess(BaseModel):
    name = db.StringProperty(required=True)
    description = db.TextProperty()

    def __unicode__(self):
        return self.name

class Member(BaseModel):
    """ Member model """
    user = db.UserProperty()
    nick = db.StringProperty(required=True)
    email = db.EmailProperty()
    role_id = db.IntegerProperty(default=roles['member'])
    active = db.BooleanProperty(default=True)

    mess = db.ReferenceProperty(Mess, required=True)

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

    @staticmethod
    def filter_mess(query):
        if not users.is_current_user_admin():
            user = Member.current_user()
            if user:
                query.filter('mess =', user.mess)
        return query

class Meal(BaseModel):
    breakfast = db.BooleanProperty(required=False)
    lunch = db.BooleanProperty(required=False)
    supper = db.BooleanProperty(required=False)
    extra = db.FloatProperty(required=False)

    date = db.DateProperty()
    member = db.ReferenceProperty(Member, required=False)

    @staticmethod
    def day_total(date):
        if users.is_current_user_admin():
            members = Member.all()
        else:
            member = Member.current_user()
            members = Member.all().filter('mess =', member.mess)
        return Meal._total_dict(members, date)

    @staticmethod
    def month_total(month, year):
        month = int(month)
        year = int(year)
        start = datetime.date(year=year, month=month, day=1)
        month += 1
        if month > 12:
            month = 1
            year += 1
        end = datetime.date(year=year, month=month, day=1)

        if users.is_current_user_admin():
            members = Member.all()
        else:
            member = Member.current_user()
            members = Member.all().filter('mess =', member.mess)

        return Meal._total_dict(members, start, end)

    @staticmethod
    def _total_dict(members, start, end=None):
        total = {
            'member': {},
            'breakfast': 0,
            'lunch': 0,
            'supper': 0,
            'extra': 0.0,
            'cost': 0.0,
        }

        for member in members:
            member_key = member.key()
            t_member = total['member'][member_key] = {
                'nick': member.nick,
            }

            if end:
                meals = member.meal_set.filter('date >=', start).filter('date <', end)
                bazaar = member.bazaar_set.filter('date >=', start).filter('date <', end)
                for b in bazaar:
                    total['cost'] += b.amount
            else:
                meals = member.meal_set.filter('date =', start)

            t_member.update(Meal.total_member(meals))

            total['breakfast'] += t_member['breakfast']
            total['lunch'] += t_member['lunch']
            total['supper'] += t_member['supper']
            total['extra'] += t_member['extra']


        total['total'] = total['breakfast'] + total['lunch'] + total['supper'] + total['extra']
        total['members'] = len(total['member'])
        if total['total'] != 0:
            total['rate'] = total['cost'] / total['total']
            if total['rate'] != 0:
                for key, value in total['member'].iteritems():
                    value['cost'] = value['total']*total['rate']
        return total

    @staticmethod
    def total_member(meals):
        total = {
            'breakfast': 0,
            'lunch': 0,
            'supper': 0,
            'extra': 0,
            'total':0,
        }
        for meal in meals:
            if meal.breakfast:
                total['breakfast'] += 1
            if meal.lunch:
                total['lunch'] += 1
            if meal.supper:
                total['supper'] += 1
            if meal.extra:
                total['extra'] += meal.extra

        total['total'] = total['breakfast'] + total['lunch'] + total['supper'] + total['extra']

        return total

class Bazaar(BaseModel):
    member = db.ReferenceProperty(Member, required=True)
    date = db.DateProperty(required=True)
    amount = db.FloatProperty(required=True)
    description = db.TextProperty()
