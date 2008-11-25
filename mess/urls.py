from django.conf.urls.defaults import *

urlpatterns = patterns('mess.views',
    (r'^member/$', 'members'),
    (r'^member/create/$', 'create_member'),
    (r'^member/edit/(.*)/$', 'edit_member'),
    (r'^member/delete/(.*)/$', 'delete_member'),

    (r'^meals/$', 'show_calendar'),
    (r'^meals/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', 'manage_meal'),

    (r'^register/$', 'register'),
)
