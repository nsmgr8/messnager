# -*- coding: utf-8 -*-

# The MIT License
# 
# Copyright (c) 2008 M. Nasimul Haque
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib
import hashlib
import logging
import datetime

from google.appengine.ext import db
from google.appengine.api import users

from appengine_django.models import BaseModel

from django.utils.html import escape
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

roles = {
    'member': 0,
    'manager': 1,
}

class Mess(BaseModel):
    name = db.StringProperty(verbose_name=_('Name'), required=True)
    description = db.TextProperty(verbose_name=_('Description'))
    breakfast = db.BooleanProperty(verbose_name=_('Half breakfast'), default=True)
    language = db.StringProperty(verbose_name=_('Language'), default='en-us')

    def __unicode__(self):
        return self.name

class Member(BaseModel):
    """ Member model """
    user = db.UserProperty(required=False)
    nick = db.StringProperty(verbose_name=_('Nickname'), required=True)
    email = db.EmailProperty(verbose_name=_('Email'), required=True)
    role_id = db.IntegerProperty(default=roles['member'])
    active = db.BooleanProperty(verbose_name=_('Active'), default=True)

    mess = db.ReferenceProperty(Mess, required=True)

    def __unicode__(self):
        return "%s (%s)" % (self.nick, self.mess.name)

    @staticmethod
    def current_user():
        user = users.get_current_user()
        if users.is_current_user_admin():
            return None
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
                    return handler_method(self, *args, **kwargs)

                user = Member.current_user()
                if not user:
                    logging.info("User not logged in -- force login")
                    return HttpResponseRedirect(users.create_login_url('/'))
                elif role == 'member' or \
                    (role == 'manager' and user.role_id == roles['manager']):
                        logging.info("Allowing role (%s) for (%s)" % (role, user.nick))
                        return handler_method(self, *args, **kwargs)
                elif role == 'active' and user.active:
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
    def month_total(month, year, key):
        month = int(month)
        year = int(year)
        start = datetime.date(year=year, month=month, day=1)
        month += 1
        if month > 12:
            month = 1
            year += 1
        end = datetime.date(year=year, month=month, day=1)

        if users.is_current_user_admin():
            if key:
                mess = Mess.get(key)
                members = Member.all().filter('mess =', mess)
            else:
                members = Member.all()
        else:
            member = Member.current_user()
            members = Member.all().filter('mess =', member.mess)

        return Meal._total_dict(members, start, end, key)

    @staticmethod
    def _total_dict(members, start, end=None, key=None):
        total = {
            'member': {},
            'breakfast': 0,
            'lunch': 0,
            'supper': 0,
            'extra': 0,
            'cost': 0,
            'bazaar': [],
        }

        for member in members:
            member_key = member.key()
            t_member = total['member'][member_key] = {
                'nick': member.nick,
            }

            meals = member.meal_set
            if end:
                meals = meals.filter('date >=', start).filter('date <', end)
            else:
                meals = meals.filter('date =', start)

            if users.is_current_user_admin() and not key:
                pass
            else:
                bazaar = member.bazaar_set
                if end:
                    bazaar = bazaar.order('date').filter('date >=', start).filter('date <', end)
                else:
                    bazaar = bazaar.filter('date =', start)
                for b in bazaar:
                    total['cost'] += b.amount
                    total['bazaar'].append({
                        'nick': b.member.nick,
                        'date': b.date,
                        'description': b.description,
                        'amount': b.amount,
                    })

            t_member.update(Meal.total_member(meals))

            total['breakfast'] += t_member['breakfast']
            total['lunch'] += t_member['lunch']
            total['supper'] += t_member['supper']
            total['extra'] += t_member['extra']


        total['total'] = total['lunch'] + total['supper'] + total['extra']
        user = Member.current_user()
        if user:
            if user.mess.breakfast:
                total['total'] += total['breakfast'] / 2.
            else:
                total['total'] += total['breakfast']
        else:
            total['total'] += total['breakfast'] / 2.

        total['members'] = len(total['member'])

        if end:
            if total['total'] != 0 and total['cost'] != 0:
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

        total['total'] = total['lunch'] + total['supper'] + total['extra']
        user = Member.current_user()
        if user:
            if user.mess.breakfast:
                total['total'] += total['breakfast'] / 2.
            else:
                total['total'] += total['breakfast']
        else:
            total['total'] += total['breakfast'] / 2.

        return total

class Bazaar(BaseModel):
    member = db.ReferenceProperty(Member, required=True)
    date = db.DateProperty(required=True)
    amount = db.FloatProperty(verbose_name=_('Amount'), required=True)
    description = db.TextProperty(verbose_name=_('Description'))
