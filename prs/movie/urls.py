from django.conf.urls import patterns, url, include
from movie import views

urlpatterns = patterns('',
	url(r'^genre/(?P<genre_name>[a-zA-Z\-]+)$', views.genre, name='genres'),
	url(r'^movie/(?P<movie_id>\d+)/$', views.detail, name='detail'),
	url(r'^$', views.index, name='index'),
	url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
)