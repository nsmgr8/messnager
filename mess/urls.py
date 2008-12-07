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

from django.conf.urls.defaults import *

import datetime

today = datetime.date.today()

urlpatterns = patterns('mess.views',
    (r'^$', 'home'),

    (r'^mess/$', 'mess_list'),
    (r'^mess/add/$', 'mess_add'),
    (r'^mess/view/$', 'mess_view'),
    (r'^mess/edit/$', 'mess_edit'),
    (r'^mess/edit/(?P<key>.*)/$', 'mess_edit'),
    (r'^mess/delete/(?P<key>.*)/$', 'mess_delete'),

    (r'^member/$', 'member_list'),
    (r'^member/create/$', 'create_member'),
    (r'^member/edit/(?P<key>.*)/$', 'edit_member'),
    (r'^member/delete/(.*)/$', 'delete_member'),
    (r'^member/(?P<key>.*)/(?P<year>\d{4})-(?P<month>\d{1,2})/$', 'member_monthly'),
    (r'^manager/$', 'assign_manager'),

    (r'^(?P<task>meals|daily|bazaar)/$', 'show_calendar', {'year':today.year,'month':today.month}),
    (r'^(?P<task>meals|daily|bazaar)/(?P<year>\d{4})-(?P<month>\d{1,2})/$', 'show_calendar'),
    (r'^bazaar/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'bazaar_daily'),
    (r'^daily/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'meal_daily'),
    (r'^meals/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'edit_meal'),
    (r'^monthly/$', 'meal_monthly', {'year':today.year,'month':today.month}),
    (r'^monthly/(?P<year>\d{4})-(?P<month>\d{1,2})/$', 'meal_monthly'),

    (r'^register/$', 'register'),
    (r'^logout/$', 'logout'),
)
