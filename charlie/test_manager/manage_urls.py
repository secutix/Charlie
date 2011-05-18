from django.conf.urls.defaults import *

urlpatterns = patterns('test_manager.views',
    (r'home_tcsc/$', 'home_tcsc'),
    (r'home/$', 'home'),
    (r'home$', 'home'),
    (r'$', 'home'),
)
