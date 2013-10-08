from django.views import generic
from django.views.generic import TemplateView
from django.db.models import Min
from sportsrec.models import *
from django.shortcuts import redirect,render
from django.contrib.auth import authenticate, login, logout
from django.http import *
from sportsrec.forms import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required

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
                    next_location = form.cleaned_data['next_location']
                    if next_location and next_location.startswith("/"):
                        return redirect(next_location)
                    return redirect('sportsrec:index')
            else:
                form = LoginForm() #Clear the form
                msg = "Invalid login details."
    else:
        form = LoginForm()
        if 'next' in request.GET:
            form.fields["next_location"].initial = request.GET['next']

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
            user.full_clean()
            user.save()

            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
            
            return redirect('sportsrec:register_thanks')
    else:
        form = RegistrationForm()
        
    return render(request, 'sportsrec/register.html', {'form' : form})

@login_required
def register_thanks(request):
    if not request.user.first_name and not request.user.last_name:
        name = request.user.username
    else:
        name = request.user.first_name + " " + request.user.last_name
    return render(request, 'sportsrec/thanks.html', {'name' : name})

@login_required
def user_profile(request):
    siteuser = SiteUser.objects.get(user=request.user)
    profile = Contact.objects.get(siteuser=siteuser)
    context = {
        'created' : False, 'name' : 'user profile',
        'view' : 'sportsrec:user_profile',
        'submit' : 'Submit'
    }

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance = profile)
        if form.is_valid():
            form.save()
            context['pass'] = "Updated successfully!"
    else:
        form = UserProfileForm(instance = profile)

    context['form'] = form
    return render(request, 'sportsrec/edit.html', context)


class Index(generic.TemplateView):
    template_name='sportsrec/index.html'
    context_object_name='index'


