from django.views import generic
from django.views.generic import TemplateView
from django.db.models import Min
from sportsrec.models import *
from django.shortcuts import redirect,render
from django.contrib.auth import authenticate, login, logout
from django.http import *
from sportsrec.forms import RegistrationForm, LoginForm
from django.contrib.auth.models import User, Group

'''
For validators
https://docs.djangoproject.com/en/dev/ref/validators/
'''

def login_user(request):
    if request.user.is_authenticated():
        return redirect('sportsrec:index')
    
    logout(request)

    msg = None
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('sportsrec:index')
            else:
                form = LoginForm() #Clear the form
                msg = "Invalid login details."
    else:
        form = LoginForm()

    return render(request, 'sportsrec/login.html',
                  {'form' : form, 'result' : msg})

def logout_user(request):
    logout(request)
    return redirect('sportsrec:index')

def register(request):
    if request.user.is_authenticated():
        return redirect('sportsrec:index')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        #do shit with it
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.groups = [Group.objects.get(name="End User")]

            #need try catch????
            user.save()
            user.full_clean()

            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
            
            return redirect('sportsrec:register_thanks')
    else:
        form = RegistrationForm()
        
    return render(request, 'sportsrec/register.html', {'form' : form})

def register_thanks(request):
    if request.user.is_authenticated():
        if not request.user.first_name and not request.user.last_name:
            name = request.user.username
        else:
            name = request.user.first_name + " " + request.user.last_name
        return render(request, 'sportsrec/thanks.html', {'name' : name})
    return redirect('sportsrec:register')


class Index(generic.TemplateView):
    template_name='sportsrec/index.html'
    context_object_name='index'


