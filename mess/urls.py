from django.conf.urls.defaults import *

urlpatterns = patterns('mess.views',
    (r'^$', 'home'),

    (r'^member/$', 'members'),
    (r'^member/create/$', 'create_member'),
    (r'^member/edit/(?P<key>.*)/$', 'edit_member'),
    (r'^member/delete/(.*)/$', 'delete_member'),
    (r'^manager/$', 'assign_manager'),

    (r'^meals/(?P<task>edit|view)/$', 'show_calendar'),
    (r'^meals/edit/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'edit_meal'),
    (r'^meals/view/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'meal_daily'),
    (r'^meals/view/(?P<year>\d{4})-(?P<month>\d{1,2})/$', 'meal_monthly'),

    (r'^register/$', 'register'),
)
