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

from django import template
from django.utils.translation import get_language

register = template.Library()

@register.filter
def beng_numeral(value):
    if not get_language() == 'bn':
        return value

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
    class BengaliLocalException:
        pass
    if not get_language() == 'bn':
        raise BengaliLocalException

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
    if not get_language() == 'bn':
        month_names = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
           10: 'October',
           11: 'November',
           12: 'December',
        }

        return month_names[value]

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
    if not get_language() == 'bn':
        weekdays = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday',
        }
        return weekdays[value]

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

