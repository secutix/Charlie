from django.conf.urls.defaults import *

urlpatterns = patterns('test_manager.views',
    (r'planning/$', 'manage_planning'),
    (r'avails/$', 'manage_avails'),
    (r'view_hist/$', 'view_hist'),
    (r'home/$', 'home'),
    (r'home$', 'home'),
    (r'$', 'home'),
)
