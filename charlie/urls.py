from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon\.ico', 'django.views.generic.simple.redirect_to', {'url': '/media/favicon.ico'}),
    (r'^admin/', include(admin.site.urls)),
    (r'^/$', 'test_manager.views.planning'),
    (r'^$', 'test_manager.views.planning'),
    (r'^test_manager/', include('test_manager.urls')),
)
