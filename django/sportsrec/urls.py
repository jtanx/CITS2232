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
    url(r'^user/members$', views.UserMemberView.as_view(), name='user_members'),
    url(r'^user/member/add$', views.user_member_add, name='user_member_add'),
    url(r'^user/member/edit/(?P<pk>\d+)$', views.user_member_edit, \
        name='user_member_edit'),
    url(r'^user/member/delete/(?P<pk>\d+)$', views.user_member_delete, \
        name='user_member_delete')
)
