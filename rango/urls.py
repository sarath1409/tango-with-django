from django.conf.urls import include, url
from rango import views
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url('about/', views.about, name='about'),
	url(r"^category/(?P<category_name_url>\w+)/$", views.category, name='category'),
	url(r'^add_category/$', views.add_category, name='add_category'),
	url(r'^category/(?P<category_name_url>\w+)/add_page/$', views.add_page, name='add_page'),
	url(r"^page/(?P<page_name_url>\w+)/$", views.page, name='page'),
	url(r'^register/$', views.register, name='register'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^restricted/', views.restricted, name='restricted'),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^generic_search/$', views.generic_search, name='generic_search'),
	url(r'^profile/$', views.profile, name='profile'),
	url(r'^goto/$', views.track_url, name='track_url'),
	url(r'^like_category/$', views.like_category, name='like_category'),
	]