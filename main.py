#!/usr/bin/env python
#
# Copyright (c) 2008 Muhammad Nasimul Haque
#

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from urls import routes

def main():
    application = webapp.WSGIApplication(routes, debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
