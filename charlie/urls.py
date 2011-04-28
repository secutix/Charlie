from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon\.ico', 'django.views.generic.simple.redirect_to', {'url': '/media/favicon.ico'}),
    (r'^tests/create_tc/', 'test_manager.views.create_tc'),
    (r'^tests/login/', 'test_manager.views.login'),
    (r'^tests/loginAttempt/', 'test_manager.views.login_attempt'),
    (r'^admin/', include(admin.site.urls)),
)
