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

import logging
import datetime
import calendar

# appengine import
from google.appengine.api import users

# django imports
from django import forms as djforms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _

# appengine_django imports
#from appengine_django.auth.models import User

# my imports
from models import *
from forms import *

def user_info():
    user = Member.current_user()
    admin = users.is_current_user_admin()

    return {
        'user': user,
        'admin': admin,
        'admin_nick': admin and users.get_current_user().nickname(),
        'manager': user and user.role_id == roles['manager'],
        'roles': roles,
        'login_url': users.create_login_url('/register/'),
        'logout_url': users.create_logout_url('/'),
    }

def render(request, template_name, params=None):
    """ render template including user information """
    paths = (
        ('/', 'home'),
        ('/mess', 'mess'),
        ('/member', 'member'),
        ('/bazaar', 'bazaar'),
        ('/daily', 'daily'),
        ('/monthly', 'monthly'),
        ('/meals', 'meals'),
        ('/manage', 'manager'),
    )
    
    for p in paths:
        if request.path.startswith(p[0]):
            current_menu = p[1]

    params = params or {}
    today = datetime.date.today()
    params.update({
        'current_month': today.month,
        'current_year': today.year,
        'current_menu': current_menu,
    })
    params.update(user_info())

    return render_to_response(template_name, params)

def home(request):
    return render(request, "home.html")

def mess_list(request):
    mess = Mess.all()
    params = {
        'mess': mess,
    }
    return render(request, 'mess_list.html', params)

def mess_view(request, key=None):
    if key:
        mess = Mess.get(key)
    else:
        try:
            mess = Member.current_user().mess
        except:
            return HttpResponseRedirect('/mess/')
    params = { 'mess': mess }
    return render(request, "mess_view.html", params)

@Member.role('admin')
def mess_add(request):
    if request.method == 'POST':
        form = MessForm(data=request.POST)
        if form.is_valid():
            form.save(commit=False).put()
            return HttpResponseRedirect('/mess/')
    else:
        form = MessForm()
    params = {
        'form': form,
    }
    return render(request, "mess_add.html", params)

@Member.role('manager')
def mess_edit(request, key=None):
    if key:
        mess = Mess.get(key)
    else:
        mess = Member.current_user().mess
    if request.method == 'POST':
        form = MessForm(data=request.POST, instance=mess)
        if form.is_valid():
            entity = form.save(commit=False)
            try:
                other = Mess.all().filter('name =', entity.name).get()
                if other and mess != other:
                    form._errors['name'] = {_("mess exists"): _("mess exists")}
                    raise
                entity.put()
                return HttpResponseRedirect('/mess/view/')
            except:
                pass
    else:
        form = MessForm(instance=mess)
    params = {
        'form': form,
    }
    return render(request, "mess_add.html", params)

@Member.role('admin')
def mess_delete(request, key):
    mess = Mess.get(key)
    if not mess:
        return HttpResponseRedirect('/mess/')
    
    members = Member.all().filter('mess =', mess)
    for member in members:
        for bazaar in member.bazaar_set:
            bazaar.delete()
        for meal in member.meal_set:
            meal.delete()
        member.delete()
    
    mess.delete()
    return HttpResponseRedirect('/mess/')

@Member.role('member')
def member_list(request):
    members = Member.all().order('-active').order('nick')
    members = Member.filter_mess(members)
    today = datetime.date.today()
    params = {
        'members': members,
        'month': today.month,
        'year': today.year,
    }
    return render(request, "member_list.html", params)

@Member.role('manager')
def create_member(request):
    if request.method == 'POST':
        if users.is_current_user_admin():
            form = MemberFormAdmin(data=request.POST)
        else:
            form = MemberForm(data=request.POST)
        
        try:
            if form.is_valid():
                entity = form.save(commit=False)
                member = Member.all().filter('email =', entity.email).get()
                if member:
                    form._errors['email'] = {_("user exists"): _("user exists")}
                    raise
                member = Member.all().filter('nick =', entity.nick).get()
                if member:
                    form._errors['nick'] = {_("user exists"): _("user exists")}
                    raise
                entity.put()
                return HttpResponseRedirect('/member/')
        except:
            pass
    else:
        if users.is_current_user_admin():
            form = MemberFormAdmin()
        else:
            user = Member.current_user()
            form = MemberForm(initial={'mess': user.mess.key()})

    return render(request, "member_add.html", {'form':form})

@Member.role('manager')
def edit_member(request, key):
    member = Member.get(key)
    if not member:
        return HttpResponseRedirect('/member/')

    if request.method == 'POST':
        form = MemberForm(data=request.POST, instance=member)
        if form.is_valid():
            try:
                entity = form.save(commit=False)
                other = Member.all().filter('email =', entity.email).get()
                if other and member != other:
                    form._errors['email'] = {_("user exists"): _("user exists")}
                    raise
                other = Member.all().filter('nick =', entity.nick).get()
                if other and  member != other:
                    form._errors['nick'] = {_("user exists"): _("user exists")}
                    raise
                return HttpResponseRedirect('/member/')
            except:
                pass
    else:
        form = MemberForm(instance=member)

    return render(request, "member_edit.html", {'form':form})

@Member.role('admin')
def delete_member(request, key):
    if request.method != 'GET':
        raise Http404

    member = Member.get(key)
    if member:
        if not member.role_id == roles['manager']:
            if not member.user == users.get_current_user():
                logging.info("deleting member %s" % member.nick)
                member.delete()
    return HttpResponseRedirect('/member/')

def register(request):
    if users.is_current_user_admin():
        return HttpResponseRedirect('/')

    user = users.get_current_user()
    if user:
        member = Member.all().filter('user', user).get()
        if not member:
            member = Member.all().filter('email', user.email()).get()
            if member:
                member.user = user
                member.put()
            else:
                logging.info('User (%s) is not allowed' % users.get_current_user())
                return HttpResponseRedirect(users.create_logout_url('/'))

    return HttpResponseRedirect('/')

def logout(request):
    return HttpResponseRedirect(users.create_logout_url('/'))

@Member.role('manager')
def assign_manager(request):
    if request.method == 'POST':
        formset = ManagerFormSet(data=request.POST)
        if formset.is_valid():
            for form in formset.forms:
                try:
                    member = Member.get(form.cleaned_data['member'])
                    if member:
                        member.role_id = form.cleaned_data['role_id'] and \
                                         roles['manager'] or roles['member']
                        member.put()
                except KeyError:
                    pass

            return HttpResponseRedirect('/member/')

        forms = zip(Member.all().order('nick'), formset.forms)
    else:
        members = Member.all().order('nick').filter('active =', True)
        members = Member.filter_mess(members)
        data = []
        for member in members:
            d = {'member': member.key()}
            if member.role_id == roles['manager']:
                d.update({'role_id': 'on'})
            data.append(d)
        formset = ManagerFormSet(initial=data)
        forms = zip(members, formset.forms)

    params = {
        'forms': forms,
        'management_form': formset.management_form,
    }

    return render(request, "assign_manager.html", params)

def _months(year, month):
    iyear = int(year)
    imonth = int(month)
    next = imonth + 1
    nexty = iyear
    if next > 12:
        next = 1
        nexty += 1
    prev = imonth - 1
    prevy = iyear
    if prev < 1:
        prev = 12
        prevy -= 1

    return {
        'month': imonth,
        'year': year,
        'current': '%s-%s' % (year, month),
        'next': '%d-%d' % (nexty, next),
        'previous': '%d-%d' % (prevy, prev),
    }

def month_calendar(year, month):
    year = int(year)
    month = int(month)

    today = datetime.date.today()
    show_month = datetime.date(year=year, month=month, day=today.day)

    if show_month == today:
        today = today.day
    else:
        today = None

    params = {
        'calendar': calendar.monthcalendar(show_month.year, show_month.month),
        'today': today,
    }
    params.update(_months(year, month))
    return params

@Member.role('member')
def show_calendar(request, task, year, month):
    params = month_calendar(year, month)
    params.update({'task': task})
    return render(request, "calendar.html", params)

@Member.role('manager')
def edit_meal(request, year, month, day):
    year = int(year)
    month = int(month)
    day = int(day)
    try:
        date = djforms.DateField()
        s_date = "%d-%d-%d" % (year, month, day)
        date = date.clean(s_date)
    except djforms.ValidationError:
        return HttpResponseRedirect('/meals/')

    if request.method == 'POST':
        formset = MealFormSet(data=request.POST)
        if formset.is_valid():
            meals = Meal.all().filter('date =', date)
            for meal in meals:
                meal.delete()
            for form in formset.forms:
                try:
                    meal = Meal()
                    meal.member = Member.get(form.cleaned_data['member'])
                    meal.breakfast = form.cleaned_data['breakfast']
                    meal.lunch = form.cleaned_data['lunch']
                    meal.supper = form.cleaned_data['supper']
                    meal.extra = float(form.cleaned_data['extra'] or 0)
                    meal.date = date
                    meal.put()
                except KeyError:
                    pass
            return HttpResponseRedirect('/meals/')

        forms = zip(Member.all().order('nick'), formset.forms)
    else:
        members = Member.all().order('nick').filter('active =', True)
        members = Member.filter_mess(members)
        data = []
        for member in members:
            d = {
                'member': member.key(),
                'extra': '0',
            }
            meals = member.get_meal(date)
            if meals:
                if meals.breakfast:
                    d.update({'breakfast': 'on',})
                if meals.lunch:
                    d.update({'lunch': 'on',})
                if meals.supper:
                    d.update({'supper': 'on',})
                d.update({'extra': str(meals.extra),})

            data.append(d)

        formset = MealFormSet(initial=data)
        forms = zip(members, formset.forms)

    params = {
        'date': '%d/%d/%d' % (day, month, year),
        'weekday': calendar.weekday(year, month, day),
        'forms': forms,
        'management_form': formset.management_form,
    }
    return render(request, "manage_meal.html", params)

@Member.role('member')
def meal_daily(request, year, month, day):
    year = int(year)
    month = int(month)
    day = int(day)
    try:
        show_day = datetime.date(year=year, month=month, day=day)
    except ValueError:
        return HttpResponseRedirect('/daily/')

    params = {
        'date': '%d/%d/%d' % (day, month, year),
        'weekday': calendar.weekday(year, month, day),
        'total': Meal.day_total(show_day),
    }
    return render(request, "meal_daily.html", params)

@Member.role('member')
def meal_monthly(request, year, month, key=None):
    params = _months(year, month)
    params['total'] = Meal.month_total(year=year, month=month, key=key)
    params['key'] = key
    return render(request, "meal_monthly.html", params)

@Member.role('member')
def member_monthly(request, key, year, month):
    member = Member.get(key)
    if not member:
        return HttpResponseRedirect('/member/')

    user = Member.current_user()
    if not users.is_current_user_admin():
        if member.mess != user.mess:
            return HttpResponseRedirect('/member/')

    params = _months(year, month)

    month = int(month)
    year = int(year)
    start = datetime.date(year=year, month=month, day=1)
    month += 1
    if month > 12:
        month = 1
        year += 1
    end = datetime.date(year=year, month=month, day=1)

    meals = member.meal_set.filter('date >=', start).filter('date <', end).order('date').fetch(32)
    params.update({
        'member': member,
        'meals': meals,
        'total': Meal.total_member(meals),
    })

    return render(request, "member_monthly.html", params)

@Member.role('active')
def bazaar_daily(request, year, month, day):
    iyear = int(year)
    imonth = int(month)
    iday = int(day)
    try:
        date = datetime.date(iyear, imonth, iday)
        today = datetime.date.today()
        if today < date:
            raise
    except:
        return HttpResponseRedirect('/bazaar/')

    if request.method == 'POST':
        if users.is_current_user_admin():
            form = BazaarFormAdmin(data=request.POST)
        else:
            form = BazaarForm(data=request.POST)
        if form.is_valid():
            member = users.is_current_user_admin() and \
                     form.cleaned_data['member'] or Member.current_user()
            amount = form.cleaned_data['amount']
            bazaar = Bazaar(member=member, date=date, amount=amount)
            bazaar.put()
            return HttpResponseRedirect('/bazaar/')
    else:
        if users.is_current_user_admin():
            form = BazaarFormAdmin()
        else:
            form = BazaarForm()

    params = {
        'form': form,
        'date': '%s/%s/%s' % (day, month, year),
        'weekday': calendar.weekday(iyear, imonth, iday),
    }

    return render(request, "bazaar_daily.html", params)
