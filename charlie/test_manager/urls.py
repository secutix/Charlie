from django.conf.urls.defaults import *

urlpatterns = patterns('test_manager.views',
    (r'availabilities/$', 'availabilities'),
    (r'create_tc/$', 'create_tc'),
    (r'planning/$', 'planning'),
    (r'do_test/$', 'do_test'),
    (r'monitoring/$', 'monitoring'),
    (r'config/$', 'config_opts'),
    (r'$', 'planning'),
)
