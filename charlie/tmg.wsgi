import os, sys
# set the path to the charlie django app here :
app_home = '/home/charlie/code/charlie/charlie'

sys.path.append('/usr/lib/pymodules/python2.6/django/')
sys.path.append(app_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
