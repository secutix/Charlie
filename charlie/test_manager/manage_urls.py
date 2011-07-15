from django.conf.urls.defaults import *

urlpatterns = patterns('test_manager.views',
    (r'current/$', 'manage_planning'),
    (r'home/$', 'home'),
    (r'home$', 'home'),
    (r'$', 'home'),
)
