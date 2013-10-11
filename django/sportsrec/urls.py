from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from sportsrec import views

urlpatterns = patterns('',
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^login/?$', views.login_user, name='login'),
    url(r'^logout$', views.logout_user, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^user/profile$', views.user_profile, name='user_profile'),
    url(r'^user/members$', views.MemberList.as_view(), name='members'),
    url(r'^user/member/add$', views.member_add, name='member_add'),
    url(r'^user/member/edit/(?P<pk>\d+)$', views.member_edit, \
        name='member_edit'),
    url(r'^user/member/delete/(?P<pk>\d+)$', views.member_delete, \
        name='member_delete'),
    url(r'^club/add$', views.club_add, name='club_add'),
    url(r'^club/list$', views.ClubList.as_view(), name='club_list'),
    url(r'^club/details/(?P<pk>\d+)$', views.club_detail, name='club_detail'),
    url(r'^memberships/list$', views.MembershipList.as_view(), \
        name='membership_list'),
    url(r'^membership/edit/(?P<pk>\d+)$', views.membership_edit, \
        name='membership_edit'),
)
