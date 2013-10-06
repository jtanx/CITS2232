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
from sportsrec.forms import UserForm, SiteUserForm

'''
For validators
https://docs.djangoproject.com/en/dev/ref/validators/
'''

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

def register_user(request):
    return render_to_response('sportsrec/register.html',
                              context_instance=RequestContext(request))

def register(request):
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        upf = SiteUserForm(request.POST, prefix='userprofile')
        if uf.is_valid() and upf.is_valid():
            user = uf.save()
            userprofile = upf.save(commit=False)
            userprofile.user = user
            userprofile.save()
            return django.http.HttpResponseRedirect('/')
    else:
        uf = UserForm(prefix='user')
        upf = SiteUserForm(prefix='userprofile')
    return render_to_response('sportsrec/register.html', 
                                dict(userform=uf,userprofileform=upf),
                                context_instance=RequestContext(request))

class Index(generic.TemplateView):
    template_name='sportsrec/index.html'
    context_object_name='index'


