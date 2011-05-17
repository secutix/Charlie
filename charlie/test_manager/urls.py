from django.conf.urls.defaults import *

urlpatterns = patterns('test_manager.views',
    (r'^availabilities/', 'availabilities'),
    (r'^create_tc/', 'create_tc'),
    (r'^create_tc_data/', 'create_tc_data'),
    (r'^create_tc_updt/', 'create_tc_updt'),
    (r'^login/', 'login_view'),
    (r'^planning/', 'planning'),
    (r'^planning_data/', 'planning_data'),
    (r'^logout/', 'logout_view'),
    (r'^$', 'planning'),
)
