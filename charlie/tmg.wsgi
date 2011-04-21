import os, sys
sys.path.append('/usr/lib/pymodules/python2.6/django/')
sys.path.append('/home/charlie/code/charlie/charlie/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
