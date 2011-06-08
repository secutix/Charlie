from django.conf.urls.defaults import *

urlpatterns = patterns('test_manager.views',
    (r'home_data/$', 'home_data'),
    (r'home_menu/$', 'home_menu'),
    (r'home/$', 'home'),
    (r'home$', 'home'),
    (r'$', 'home'),
)
