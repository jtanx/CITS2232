from django.views import generic
from django.views.generic import TemplateView
from django.db.models import Min
from sportsrec.models import *
import datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.http import *


def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
        else:
            return render_to_response('sportsrec/login.html', \
                                      {'login_failed': True}, \
                                      context_instance=RequestContext(request))
    return render_to_response('sportsrec/login.html', \
                              context_instance=RequestContext(request))

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

class Index(generic.TemplateView):
    template_name='sportsrec/index.html'
    context_object_name='index'
