# -*- coding: utf-8 -*-

import logging
import datetime
import calendar

# appengine import
from google.appengine.api import users

# django imports
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.forms.formsets import formset_factory
from django import forms as djforms

# my imports
from models import roles
from models import Member, Meal
from forms import MemberForm, MealForm

def render(template_name, params=None):
    """ render template including user information """
    user = Member.current_user()
    user_info = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'manager': user and user.role_id == roles['ম্যানেজার'],
        'roles': roles,
        'login_url': user and users.create_logout_url('/member/') or users.create_login_url('/register/'),
    }

    params = params or {}
    params.update(user_info)

    return render_to_response(template_name, params)


def members(request):
    members = Member.all().order('nick')
    return render("member_list.html", {'members': members})

@Member.role('admin')
def create_member(request):
    if request.method == 'GET':
        form = MemberForm()
        return render("member_add.html", {'form':form})

    if request.method == 'POST':
        form = MemberForm(data=request.POST)
        if form.is_valid():
            form.save(commit=False).put()
            return HttpResponseRedirect('/member/')

        return render("member_add.html", {'form':form})

@Member.role('admin')
def edit_member(request, key):
    if request.method == 'GET':
        member = Member.get(key)
        if not member:
            return HttpResponseRedirect('/member/')

        form = MemberForm(instance=member)
        return render("member_edit.html", {'form':form})

    if request.method == 'POST':
        member = Member.get(key)
        if not member:
            return HttpResponseRedirect('/member/')

        form = MemberForm(data=request.POST, instance=member)
        if form.is_valid():
            form.save(commit=False).put()
            return HttpResponseRedirect('/member/')

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
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/member/')

    user = users.User()
    member = Member.all().filter('user', user).get()

    if users.is_current_user_admin():
        if not member:
            member = Member()
            member.user = user
            member.email = user.email()
            member.nick = user.nickname()
            member.put()
        return HttpResponseRedirect('/member/')

    if not member:
        member = Member.all().filter('email', user.email()).get()
        if member:
            member.user = user
            member.put()
        else:
            logging.info('User (%s) is not allowed' % users.get_current_user())
            return HttpResponseRedirect(users.create_logout_url('/member/'))

    return HttpResponseRedirect('/member/')

def show_calendar(request):
    today = datetime.date.today()
    params = {
        'calendar': calendar.monthcalendar(today.year, today.month),
        'month': today.month,
        'year': today.year,
    }
    return render("calendar.html", params)

def manage_meal(request, year, month, day):
    MealFormSet = formset_factory(MealForm)

    try:
        date = djforms.DateField()
        s_date = "%s-%s-%s" % (year, month, day)
        date = date.clean(s_date)
    except:
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
            return HttpResponseRedirect('/member/')

        forms = zip(Member.all().order('nick'), formset.forms)
    else:
        members = Member.all().order('nick')
        data = []
        for member in members:
            d = {
                'member': str(member.key()),
                'extra': '0',
            }
            meals = Meal.all().filter('date =', date).filter('member =', member.key()).get()
            if meals:
                if meals.breakfast:
                    d.update({'breakfast': 'on',})
                if meals.lunch:
                    d.update({'lunch': 'on',})
                if meals.supper:
                    d.update({'supper': 'on',})
                d.update({'extra': str(meals.extra),})

            data.append(d)

        if len(data) == 0:
            raise Http404

        formset = MealFormSet(initial=data)
        forms = zip(members, formset.forms)

    params = {
        'forms': forms,
        'management_form': formset.management_form,
    }
    return render("manage_meal.html", params)
