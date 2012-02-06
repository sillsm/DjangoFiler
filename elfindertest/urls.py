from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from settings import MEDIA_ROOT
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'elfindertest.views.home', name='home'),
    url(r'^elfinder/', include('elfindertest.connector.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^media/(?P<path>.*)$','django.views.static.serve', {'document_root':MEDIA_ROOT}),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
