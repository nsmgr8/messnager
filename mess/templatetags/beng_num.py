# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter
def beng_numeral(value):
    trans_dict = {
        '1': '১',
        '2': '২',
        '3': '৩',
        '4': '৪',
        '5': '৫',
        '6': '৬',
        '7': '৭',
        '8': '৮',
        '9': '৯',
        '0': '০',
    }

    value = str(value)
    for e, b in trans_dict.iteritems():
        value = value.replace(e, b)

    return value

@register.filter
def beng_month(value):
    month_names = {
        1: 'বৈশাখ',
        2: 'জৈষ্ঠ্য',
        3: 'আষাড়',
        4: 'শ্রাবণ',
        5: 'ভাদ্র',
        6: 'আশ্বিন',
        7: 'কার্তিক',
        8: 'অগ্রহায়ন',
        9: 'পৌষ',
       10: 'মাঘ',
       11: 'ফাল্গুন',
       12: 'চৈত্র',
    }

    return month_names[value]

@register.filter
def eng_month(value):
    month_names = {
        1: 'জানুয়ারি',
        2: 'ফেব্রুয়ারি',
        3: 'মার্চ',
        4: 'এপ্রিল',
        5: 'মে',
        6: 'জুন',
        7: 'জুলাই',
        8: 'আগষ্ট',
        9: 'সেপ্টেম্বর',
       10: 'অক্টোবর',
       11: 'নভেম্বর',
       12: 'ডিসেম্বর',
    }

    return month_names[value]

@register.filter
def beng_weekday(value):
    weekdays = {
        0: 'সোমবার',
        1: 'মঙ্গলবার',
        2: 'বুধবার',
        3: 'বৃহস্পতিবার',
        4: 'শুক্রবার',
        5: 'শনিবার',
        6: 'রবিবার',
    }

    return weekdays[value]

@register.filter
def truncate_chars(value, by):
    l = len(value)
    if l > by:
        value = value[:by-3] + '...'

    return value

