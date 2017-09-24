from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'EventSearch.views.index', name='index'),
    url(r'^events/', 'EventSearch.views.display_events', name='events'),
    url(r'^admin/', include(admin.site.urls)),
)
