from django.conf.urls.defaults import *

urlpatterns = patterns('test_manager.views',
    (r'home_data/$', 'home_data'),
    (r'home_ts/$', 'home_ts'),
    (r'current/$', 'manage_planning'),
    (r'home_teams/$', 'home_teams'),
    (r'home_menu/$', 'home_menu'),
    (r'home/$', 'home'),
    (r'home$', 'home'),
    (r'$', 'home'),
)
