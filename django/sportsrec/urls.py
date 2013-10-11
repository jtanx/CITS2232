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
    url(r'^members$', views.MemberList.as_view(), name='members'),
    url(r'^member/(?P<pk>\d+)$', views.member_detail, \
        name='member_detail'),
    url(r'^member/add$', views.member_add, name='member_add'),
    url(r'^member/edit/(?P<pk>\d+)$', views.member_edit, \
        name='member_edit'),
    url(r'^member/delete/(?P<pk>\d+)$', views.member_delete, \
        name='member_delete'),
    url(r'^club/add$', views.club_add, name='club_add'),
    url(r'^clubs$', views.ClubList.as_view(), name='club_list'),
    url(r'^club/edit/(?P<pk>\d+)$', views.club_edit, name='club_edit'),
    url(r'^user/clubs$', views.UserClubList.as_view(), name='user_club_list'),
    url(r'^club/(?P<pk>\d+)$', views.club_detail, name='club_detail'),
    url(r'^memberships$', views.MembershipList.as_view(), \
        name='membership_list'),
    url(r'^membership/detail/(?P<pk>\d+)$', views.membership_detail, \
        name='membership_detail'),
)
