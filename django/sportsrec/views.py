from django.views import generic
from django.views.generic import TemplateView
from django.db.models import Min, Avg, Count
from sportsrec.models import *
from django.shortcuts import redirect,render
from django.contrib.auth import authenticate, login, logout
from django.http import *
from sportsrec.forms import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

'''
For validators
https://docs.djangoproject.com/en/dev/ref/validators/
'''

def login_user(request):
    if request.user.is_authenticated():
        return redirect('sportsrec:index')
    
    logout(request)

    context = {}
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
                        #Redirect to specified location, if given
                        return redirect(next_location)
                    return redirect('sportsrec:index')
            else:
                form = LoginForm() #Clear the form
                context['result'] = "Invalid login details."
    else:
        form = LoginForm()
        if 'next' in request.GET:
            form.fields["next_location"].initial = request.GET['next']

    context['form'] = form
    return render(request, 'sportsrec/login.html', context)

def logout_user(request):
    logout(request)
    return redirect('sportsrec:index')

def register(request):
    if request.user.is_authenticated():
        return redirect('sportsrec:index')

    context = {}
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
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

            user.full_clean()
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)

            context['name'] = first_name + " " + last_name
            context['thanks'] = True
    else:
        form = RegistrationForm()

    context['form'] = form
    return render(request, 'sportsrec/register.html', context)

@login_required
def user_profile(request):
    context = {
        'created' : False, 'name' : 'user profile',
        'view' : 'sportsrec:user_profile',
        'submit' : 'Submit'
    }

    user = request.user
    if request.method == "POST":
        form = UserProfileForm(user, request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            password = form.cleaned_data.get("new_password", None)
            if password:
                user.set_password(password)
            user.save()
            context['pass'] = "Updated successfully!"
    else:
        form = UserProfileForm(user)

    context['form'] = form
    return render(request, 'sportsrec/edit.html', context)

class TotalStats(generic.TemplateView):
    usercount = User.objects.filter(groups__name="End User").count()
    membercount = Member.objects.all().count()
    clubcount = Club.objects.all().count()
    membercountavg = Club.objects.all().aggregate(Avg('member_count'))
    membercountperclub = Club.objects.values('type').\
                         annotate(count=Count('type'))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TotalStats, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['stats'] = {
            'usercount' : self.usercount,
            'membercount' : self.membercount,
            'clubcount' : self.clubcount,
            'membercountavg' : self.membercountavg,
            'membercountperclub' : self.membercountperclub
        }
        return context
    

class Index(TotalStats):
    template_name='sportsrec/index.html'
    context_object_name='index'


