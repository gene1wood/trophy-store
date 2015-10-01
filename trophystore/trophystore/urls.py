from django.conf.urls import patterns, include, url
from django.contrib import admin
from django_browserid.admin import site as browserid_admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

import views

admin.autodiscover()
browserid_admin.copy_registry(admin.site)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trophystore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(browserid_admin.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^request/$', views.request, name='request'),
    url(r'^display_list/$', views.display_list, name='display_list'),
    url(r'^display_cert/([0-9]+)/$', views.display_cert, name='display_cert'),
    url(r'^deploy/$', views.deploy, name='deploy'),
    url(r'^showsettings/$', views.showsettings, name='showsettings'),
    url(r'^cacheclear/$', views.cacheclear, name='cacheclear'),
    url(r'', include('django_browserid.urls')),

)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()