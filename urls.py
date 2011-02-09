from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from django.contrib import databrowse
from woningscrape.models import *
databrowse.site.register(Gemeente)
databrowse.site.register(Woning)

if settings.DEBUG:
    from staticfiles.urls import staticfiles_urlpatterns
    
    urlpatterns = staticfiles_urlpatterns()
    
else:
    urlpatterns = patterns('')

urlpatterns += patterns('',
    #(r'^/', include('foo.urls')),
    (r'^(.*)', databrowse.site.root),

    # Django Admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)
