# -*- coding: utf-8 -*-

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
from models import roles
from models import Mess
from models import Member
from models import Meal
from models import Bazaar

from forms import MessForm
from forms import MemberForm
from forms import MemberFormAdmin
from forms import ManagerForm
from forms import MealForm
from forms import MealFormSet
from forms import ManagerFormSet
from forms import BazaarForm

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

def render(template_name, params=None):
    """ render template including user information """
    params = params or {}
    today = datetime.date.today()
    params.update({
        'current_month': today.month,
        'current_year': today.year,
    })
    params.update(user_info())

    return render_to_response(template_name, params)

def home(request):
    return render("home.html")

@Member.role('admin')
def mess_list(request):
    mess = Mess.all()
    params = {
        'mess': mess,
    }
    return render('mess_list.html', params)

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
    return render("mess_add.html", params)

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
    return render("member_list.html", params)

@Member.role('manager')
def create_member(request):
    if request.method == 'POST':
        if users.is_current_user_admin():
            form = MemberFormAdmin(data=request.POST)
        else:
            form = MemberForm(data=request.POST)
        if form.is_valid():
            entity = form.save(commit=False)
            entity.put()
            return HttpResponseRedirect('/member/')
    else:
        if users.is_current_user_admin():
            form = MemberFormAdmin()
        else:
            user = Member.current_user()
            form = MemberForm(initial={'mess': user.mess.key()})

    return render("member_add.html", {'form':form})

@Member.role('manager')
def edit_member(request, key):
    member = Member.get(key)
    if not member:
        return HttpResponseRedirect('/member/')

    if request.method == 'POST':
        form = MemberForm(data=request.POST, instance=member)
        if form.is_valid():
            form.save(commit=False).put()
            return HttpResponseRedirect('/member/')
    else:
        form = MemberForm(instance=member)

    return render("member_edit.html", {'form':form})


@Member.role('admin')
def delete_member(request, key):
    if request.method != 'GET':
        raise Http404

    member = Member.get(key)
    if member:
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

    return render("assign_manager.html", params)

def month_calendar():
    #calendar.setfirstweekday(settings.FIRST_WEEK_DAY)
    today = datetime.date.today()
    return {
        'calendar': calendar.monthcalendar(today.year, today.month),
        'today': today.day,
        'month': today.month,
        'year': today.year,
    }

@Member.role('member')
def show_calendar(request, task):
    params = month_calendar()
    params.update({'task': task})
    return render("calendar.html", params)

@Member.role('manager')
def edit_meal(request, year, month, day):
    try:
        today = datetime.date.today()
        if int(year) != today.year or int(month) != today.month:
            raise
        date = djforms.DateField()
        s_date = "%s-%s-%s" % (year, month, day)
        date = date.clean(s_date)
    except:
        return HttpResponseRedirect('/meals/edit/')

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
            return HttpResponseRedirect('/meals/edit/')

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
        'date': '%s/%s/%s' % (day, month, year),
        'weekday': calendar.weekday(int(year),int(month),int(day)),
        'forms': forms,
        'management_form': formset.management_form,
    }
    return render("manage_meal.html", params)

@Member.role('member')
def meal_daily(request, year, month, day):
    iyear = int(year)
    imonth = int(month)
    iday = int(day)
    try:
        date = datetime.date(iyear, imonth, iday)
        today = datetime.date.today()
        if iyear != today.year or imonth != today.month:
            raise
    except:
        return HttpResponseRedirect('/meals/view/')

    params = {
        'date': '%s/%s/%s' % (day, month, year),
        'weekday': calendar.weekday(iyear, imonth, iday),
        'total': Meal.day_total(date),
    }
    return render("meal_daily.html", params)

@Member.role('member')
def meal_monthly(request, year, month):
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

    params = {
        'month': imonth,
        'year': year,
        'current': '%s-%s' % (year, month),
        'next': '%d-%d' % (nexty, next),
        'previous': '%d-%d' % (prevy, prev),
        'total': Meal.month_total(year=year, month=month),
    }
    return render("meal_monthly.html", params)

@Member.role('member')
def member_monthly(request, key, year, month):
    member = Member.get(key)
    if not member:
        return HttpResponseRedirect('/member/')

    user = Member.current_user()
    if not users.is_current_user_admin():
        if member.mess != user.mess:
            return HttpResponseRedirect('/member/')

    month = int(month)
    year = int(year)
    start = datetime.date(year=year, month=month, day=1)
    month += 1
    if month > 12:
        month = 1
        year += 1
    end = datetime.date(year=year, month=month, day=1)

    meals = member.meal_set.filter('date >=', start).filter('date <', end).order('date').fetch(32)
    params = {
        'nick': member.nick,
        'meals': meals,
        'total': Meal.total_member(meals),
    }

    return render("member_monthly.html", params)

@Member.role('member')
def bazaar_daily(request, year, month, day):
    iyear = int(year)
    imonth = int(month)
    iday = int(day)
    try:
        date = datetime.date(iyear, imonth, iday)
        today = datetime.date.today()
        if iyear != today.year or imonth != today.month:
            raise
    except:
        return HttpResponseRedirect('/meals/bazaar/')

    if request.method == 'POST':
        form = BazaarForm(data=request.POST)
        if form.is_valid():
            bazaar = Bazaar(
                member=Member.current_user(),
                date=date,
                amount=form.cleaned_data['amount'])
            bazaar.put()
            return HttpResponseRedirect('/meals/bazaar/')
    else:
        form = BazaarForm()

    params = {
        'form': form,
        'date': '%s/%s/%s' % (day, month, year),
        'weekday': calendar.weekday(int(year),int(month),int(day)),
    }
    return render("bazaar_daily.html", params)
