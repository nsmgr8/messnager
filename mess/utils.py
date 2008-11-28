import os

from google.appengine.api import users, memcache
from google.appengine.ext.webapp import template

# django import
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render_to_response

from models import Member, roles

import settings

def render(template_name, params=None):
    """ render template including user information """
    user = Member.current_user()
    user_info = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'manager': user and user.role_id == roles['Manager'],
        'roles': roles,
        'login_url': user and users.create_logout_url('/member/') or users.create_login_url('/register/'),
    }

    if params is None:
        params = {}
    params.update(user_info)
    params['project'] = settings.project_info

    return render_to_response(template_name, params)

def paginate(objects, request, limit=10, name="objects"):
    """ returns context params updating by pagination """
    try:
        page = int(request.GET['page'])
    except:
        page = 1

    if cache_key:
        cache_key = "%s_page_%d" % (cache_key, page)
        params = memcache.get(cache_key)
        if params:
            return params

    paginator = Paginator(objects, limit)
    try:
        page = paginator.page(page)
    except InvalidPage:
        page = 1
        cache_key = "%s_page_0" % cache_key
        page = paginator.page(page)

    params = {
        name: page.object_list,
        'page': page,
        'the_path': request.path,
    }

    if cache_key:
        if not memcache.add(cache_key, params, settings.CACHE_TIME):
            logging.error("Couldn't set memcache for %s" % cache_key)
        else:
            logging.info("memcache set for %s" % cache_key)

    return params
