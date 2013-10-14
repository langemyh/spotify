from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'spotify.views.front', name='home'),
	url(r'^(http://open\.spotify\.com|spotify)[/:](track|album|artist)[/:]([a-zA-Z0-9]{22})/$', 'spotify.views.spotify', name='toill'),
	url(r'^spotify/$', 'spotify.views.spotify', name='spotify'),
	url(r'^playlist/$', 'spotify.views.playlist', name='playlist'),
    # url(r'^$', 'spotify.views.home', name='home'),
    # url(r'^spotify/', include('spotify.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
