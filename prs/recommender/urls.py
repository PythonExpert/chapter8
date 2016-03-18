from django.conf.urls import patterns, url, include
from recommender import views

urlpatterns = patterns('',
	url(r'^hello/', views.hello, name='hello'),
	url(r'^chart/', views.chart, name='chart'),
	url(r'^associarules/', views.get_associationrules, name='get_associationrules'),
	url(r'^itemsets/', views.itemsets_support, name='itemsets_support'),
	url(r'^build/associationrules', views.build_association_rules, name='build_association_rules'),
	url(r'^recs/(?P<userid>[a-zA-Z0-9,]+)', views.multiseeded_recs_by_userid, name='multiseeded_recs_by_userid'),
	url(r'^seeded_recs/', views.seeded_recs, name='seeded_recs'),
	url(r'^collaborative/user/(?P<userid>[a-zA-Z0-9,]+)', views.cf_user, name='user_collaborativefiltering'),
	url(r'^collaborative/item/(?P<userid>[a-zA-Z0-9,]+)', views.cf_item, name='item_collaborativefiltering'),
)