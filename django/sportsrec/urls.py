from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from sportsrec import views

urlpatterns = patterns('',
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^login$', views.login_user, name='login'),
    url(r'^logout$', views.logout_user, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^register/thanks$', views.register_thanks, name='register_thanks'),
    url(r'^club/create/$', views.create_club, name='create_club'),
	#url(r'^club/(?P<pk>\d+)/edit/$', views.edit_club, name='edit_club'),
	#url(r'^club/(?P<pk>\d+)/delete/$', views.delete_club, name='delete_club'),
	#url(r'^member/create/$', views.create_member, name='create_member'),
	#url(r'^member/(?P<pk>\d+)/edit/$', views.edit_member, name='edit_member'),
	#url(r'^member/(?P<pk>\d+)/delete/$', views.delete_member, name='delete_member'),
	url(r'^contact/edit/$', views.edit_contact, name='edit_contact'),
)
