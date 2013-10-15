from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import RedirectView
from sportsrec import views
from sportsrec import models

urlpatterns = patterns('',
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^stats$', views.StatsOverView.as_view(), name='stats'),
    url(r'^stats/clubtype$', views.ClubTypeStatsView.as_view(), name='stats_club'),
    url(r'^login/?$', views.login_user, name='login'),
    url(r'^logout$', views.logout_user, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^user/(?P<pk>\d+)$', views.UserDetailView.as_view(), name='user_detail'),
    url(r'^user/list$', views.UserListView.as_view(), name='user_list'),
    url(r'^user/profile$', views.user_profile, name='user_profile'),
    url(r'^user/promote/(?P<pk>\d+)$', views.UserPromoteView.as_view(), name='user_promote'),
    url(r'^user/demote/(?P<pk>\d+)$', views.UserDemoteView.as_view(), name='user_demote'),
    url(r'^user/disable/(?P<pk>\d+)$', views.UserDisableView.as_view(), name='user_disable'),
    url(r'^user/enable/(?P<pk>\d+)$', views.UserEnableView.as_view(), name='user_enable'),
    url(r'^user/clubs$', views.UserClubList.as_view(), name='user_club_list'),
    url(r'^user/club/applications$', views.UserClubApplicationList.as_view(),\
        name='user_club_application_list'),
    url(r'^members$', views.MemberList.as_view(), name='member_list'),
    url(r'^member/(?P<pk>\d+)$', views.MemberDetailView.as_view(), \
        name='member_detail'),
    url(r'^member/add$', views.MemberAddView.as_view(), name='member_add'),
    url(r'^member/edit/(?P<pk>\d+)$', views.member_edit, \
        name='member_edit'),
    url(r'^member/delete/(?P<pk>\d+)$', views.MemberDeleteView.as_view(), \
        name='member_delete'),
    url(r'^clubs$', views.ClubList.as_view(), name='club_list'),
    url(r'^club/add$', views.club_add, name='club_add'),
    url(r'^club/edit/(?P<pk>\d+)$', views.club_edit, name='club_edit'),
    url(r'^club/delete/(?P<pk>\d+)$',views.ClubDeleteView.as_view(), name='club_delete'),
    url(r'^club/(?P<pk>\d+)$', views.ClubDetailView.as_view(), name='club_detail'),
    url(r'^club/(?P<pk>\d+)/members$', views.ClubMembersView.as_view(), name='club_member_list'),
    url(r'^memberships$', views.MembershipList.as_view(), \
        name='membership_list'),
    url(r'^membership/apply/(?P<pk>\d+)$', views.MembershipApplyView.as_view(), \
        name='membership_apply'),
    url(r'^membership/applications$', views.MembershipApplicationView.as_view(), \
        name='membership_application_list'),
    url(r'^membership/application/delete/(?P<pk>\d+)$',\
        views.MembershipApplicationDeleteView.as_view(), \
        name='membership_application_delete'),
    url(r'^membership/detail/(?P<pk>\d+)$', views.MembershipDetailView.as_view(), \
        name='membership_detail'),
    url(r'^membership/delete/(?P<pk>\d+)$', views.MembershipDeleteView.as_view(), \
        name='membership_delete'),
    url(r'^club/search$', views.search, name='search'),
    url(r'^club/search/name$', views.SearchView.as_view(), name='search_name'),
)
