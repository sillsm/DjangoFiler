from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'elfindrtest.views.home', name='home'),
    url(r'^$', 'connector.views.index'),
    url(r'^connector$', 'connector.views.connector'),
    url(r'^sounds/', 'connector.views.sounds'),
)
