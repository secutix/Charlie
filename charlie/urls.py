from django.conf.urls.defaults import *
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon\.ico', 'django.views.generic.simple.redirect_to', {'url': '/media/favicon.ico'}),
    (r'^test_manager/availabilities/', 'test_manager.views.availabilities'),
    (r'^test_manager/create_tc/', 'test_manager.views.create_tc'),
    (r'^test_manager/create_tc_data/', 'test_manager.views.create_tc_data'),
    (r'^test_manager/login/', 'test_manager.views.login_view'),
    (r'^test_manager/planning/', 'test_manager.views.planning'),
    (r'^test_manager/planning_data/', 'test_manager.views.planning_data'),
    (r'^test_manager/logout/', 'test_manager.views.logout_view'),
    (r'^admin/', include(admin.site.urls)),
    (r'^test_manager/$', 'test_manager.views.planning'),
    (r'^test_manager$', 'test_manager.views.planning'),
    (r'^/$', 'test_manager.views.planning'),
    (r'^$', 'test_manager.views.planning'),
)
