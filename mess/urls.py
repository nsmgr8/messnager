from django.conf.urls.defaults import *

import datetime

today = datetime.date.today()

urlpatterns = patterns('mess.views',
    (r'^$', 'home'),

    url(r'^mess/$', 'mess_list', name="mess"),
    (r'^mess/add/$', 'mess_add'),

    (r'^member/$', 'member_list'),
    (r'^member/create/$', 'create_member'),
    (r'^member/edit/(?P<key>.*)/$', 'edit_member'),
    (r'^member/delete/(.*)/$', 'delete_member'),
    (r'^member/(?P<key>.*)/(?P<year>\d{4})-(?P<month>\d{1,2})/$', 'member_monthly'),
    (r'^manager/$', 'assign_manager'),

    (r'^meals/(?P<task>edit|view|bazaar)/$', 'show_calendar'),
    (r'^meals/edit/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'edit_meal'),
    (r'^meals/view/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'meal_daily'),
    (r'^meals/view/(?P<year>\d{4})-(?P<month>\d{1,2})/$', 'meal_monthly'),
    (r'^meals/view/current/$', 'meal_monthly', {'year':today.year,'month':today.month}),
    (r'^meals/bazaar/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'bazaar_daily'),

    (r'^register/$', 'register'),
)
urlpatterns += ('',
    (r'^login/$', 'django.auth.views.login'),
)
