import views

routes = [
    ('/member/$', views.Members),
    ('/member/create/$', views.CreateMember),
    ('/member/edit/(.*)/$', views.EditMember),
    ('/member/delete/(.*)/$', views.DeleteMember),

    ('/meals/$', views.ManageMeal),

    ('/register/$', views.Register),
]
