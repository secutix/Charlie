from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon\.ico', 'django.views.generic.simple.redirect_to', {'url': '/media/favicon.ico'}),
    (r'^logout', 'test_manager.views.logout_view'),
    (r'^login', 'test_manager.views.login_view'),
    # django admin interfaces :
    (r'^admin/', include(admin.site.urls)),
    # tester interfaces :
    (r'^test_manager/', include('test_manager.urls')),
    # admin custom interfaces :
    (r'^manage/', include('test_manager.manage_urls')),
    (r'^/', 'test_manager.views.planning'),
    (r'^', 'test_manager.views.planning'),
)
