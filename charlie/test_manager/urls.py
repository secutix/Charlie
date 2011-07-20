from django.conf.urls.defaults import *

urlpatterns = patterns('test_manager.views',
    (r'availabilities/$', 'availabilities'),
    (r'create_tc/$', 'create_tc'),
    (r'planning/$', 'planning'),
    (r'planning_data/$', 'planning_data'),
    (r'$', 'planning'),
)
