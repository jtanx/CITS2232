from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from sportsrec import views

urlpatterns = patterns('',
    url(r'^$', views.Index.as_view(), name='index'),
)
