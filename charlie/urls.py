from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon\.ico', 'django.views.generic.simple.redirect_to', {'url': '/media/favicon.ico'}),
    (r'^test_manager/create_tc/', 'test_manager.views.create_tc'),
    (r'^test_manager/login/', 'test_manager.views.login_view'),
    (r'^test_manager/planning/', 'test_manager.views.planning'),
    (r'^test_manager/test/', 'test_manager.views.test_lol'),
    (r'^test_manager/logout/', 'test_manager.views.logout_view'),
    (r'^admin/', include(admin.site.urls)),
)
