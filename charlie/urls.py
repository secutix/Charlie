from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^tests/create_tc/', 'test_manager.views.create_tc'),
    (r'^admin/', include(admin.site.urls)),
)
