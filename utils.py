import os

from google.appengine.api import users, memcache
from google.appengine.ext.webapp import template

# django import
from django.core.paginator import ObjectPaginator, InvalidPage

from models import Member, roles

import settings

template_path = settings.template_path

def render(handler, template_name, params=None):
    """ render template including user information """
    user = Member.current_user()
    user_info = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'manager': user and user.role_id == roles['Manager'],
        'roles': roles,
        'login_url': user and users.create_logout_url('/') or users.create_login_url('/register/'),
    }

    if params is None:
        params = {}
    params.update(user_info)
    params['project'] = settings.project_info

    template_name = os.path.join(template_path, template_name)
    handler.response.out.write(template.render(template_name, params))

def paginate(objects, handler, limit=10, name="objects", cache_key=None):
    """ returns context params updating by pagination """
    page = int(handler.request.get('page', 0))

    if cache_key:
        cache_key = "%s_page_%d" % (cache_key, page)
        params = memcache.get(cache_key)
        if params:
            return params

    paginator = ObjectPaginator(objects, limit)
    try:
        objects = paginator.get_page(page)
    except InvalidPage:
        page = 0
        cache_key = "%s_page_0" % cache_key
        objects = paginator.get_page(page)

    params = {
        name: objects,
        'has_next': paginator.has_next_page(page),
        'has_previous': paginator.has_previous_page(page),
        'page': page,
        'first': 0,
        'previous': page - 1,
        'next': page + 1,
        'last': paginator.pages - 1,
        'the_path': handler.request.path,
    }

    if cache_key:
        if not memcache.add(cache_key, params, settings.CACHE_TIME):
            logging.error("Couldn't set memcache for %s" % cache_key)
        else:
            logging.info("memcache set for %s" % cache_key)

    return params
