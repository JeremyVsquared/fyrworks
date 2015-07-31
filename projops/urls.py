from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import include, url
from django.contrib import admin

from pm import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^team/(?P<group>\d+)/$', views.dashboard),
    url(r'^team/(?P<group>\d+)/n/(?P<user>\d+).json$', views.notifications, {'notification': None, 'dismissing': False}),
    url(r'^team/(?P<group>\d+)/n/(?P<user>\d+)/(?P<notification>\d+).json$', views.notifications, {'dismissing': False}),
    url(r'^team/(?P<group>\d+)/n/(?P<user>\d+)/(?P<notification>\d+)/dismiss.json$', views.notifications, {'dismissing': True}),
    url(r'^team/(?P<group>\d+)/tasks/$', views.home),
    url(r'^team/(?P<group>\d+)/tasks/search/$', views.search),
    url(r'^team/(?P<group>\d+)/tasks/search.(?P<output_format>xml|json)$', views.search),
    url(r'^team/(?P<group>\d+)/tasks/(?P<id>\d+)/$', views.task),
    url(r'^team/(?P<group>\d+)/tasks/(?P<id>\d+)/comments/$', views.task_comment),
    url(r'^team/(?P<group>\d+)/tasks/add/$', views.task_add),
    url(r'^team/(?P<group>\d+)/tags/(?P<tag>\d+)/$', views.tags),
    url(r'^team/(?P<group>\d+)/tags/$', views.tags, {'tag': None}),
    url(r'^team/(?P<group>\d+)/analytics/$', views.analytics),
    url(r'^team/(?P<group>\d+)/settings/$', views.settings),
    url(r'^login/$', views.login_page),
    url(r'^signup/$', views.signup),
    url(r'^$', views.public_home),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
