from django.conf.urls import patterns, include, url
from treeer.views import ThreadDetail

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^(?P<pk>\d+)$', ThreadDetail.as_view(), name='thread'),
    # url(r'^threadedcomms/', include('threadedcomms.foo.urls')),
)
