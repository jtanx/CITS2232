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
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.contrib import messages
from sportsrec.admin import is_admin

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
    return render(request, 'sportsrec/add_edit.html', context)

@login_required
def user_member_add(request):
    context = {
        'created' : True, 'name' : 'member',
        'view' : 'sportsrec:user_member_add',
        'submit' : 'Add'
    }
    
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            #Don't save yet
            member = form.save(commit=False)
            #Tack on the owner
            member.owner = request.user
            member.save()
            messages.add_message(request, messages.INFO, \
                                 "Member successfully created!")
            return redirect('sportsrec:user_members')
    else:
        form = MemberForm()

    context['form'] = form

    return render(request, 'sportsrec/add_edit.html', context)
            

@login_required
def user_member_edit(request, pk):
    member = Member.objects.filter(pk=pk)
    if not member.exists():
        messages.add_message(request, messages.ERROR, \
                             "Member does not exist.")
        return redirect('sportsrec:user_members')

    member = member[0]
    
    if not member.owner == request.user and not is_admin(request.user):
        messages.add_message(request, messages.ERROR, \
                             "You can't edit a member you didn't create.")
        return redirect('sportsrec:user_members')

    context = {
        'created' : False,
        'name' : 'member details',
        'view' : 'sportsrec:user_member_edit',
        'delete_view' : 'sportsrec:user_member_delete',
        'delete_text' : 'this member',
        'pk' : pk,
        'submit' : 'Edit'
    }

    if request.method == "POST":
        form = MemberForm(request.POST, instance = member)
        if form.is_valid():
            form.save()
            context['pass'] = "Updated successfully!"
    else:
        form = MemberForm(instance = member)

    context['form'] = form

    return render(request, 'sportsrec/add_edit.html', context)

@login_required
def user_member_delete(request, pk):
    member = Member.objects.filter(pk=pk)
    if not member.exists():
        messages.add_message(request, messages.ERROR, \
                             "Member does not exist.")
        return redirect('sportsrec:user_members')

    member = member[0]
    
    if not member.owner == request.user and not is_admin(request.user):
        messages.add_message(request, messages.ERROR, \
                             "You can't delete a member you didn't create.")
        return redirect('sportsrec:user_members')
    
    context = {
        'name' : "member: '%s'" % member,
        'view' : 'sportsrec:user_member_delete',
        'pk' : pk,
        'form' : DeleteForm(),
        'submit' : 'Submit'
    }

    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['confirm']:
                member.delete()
                messages.add_message(request, messages.INFO, \
                             "Member deleted successfully!")
        return redirect('sportsrec:user_members')
    
    return render(request, 'sportsrec/delete.html', context)

@login_required
def club_add(request):
	context = {
		'created' : True, 'name' : 'club',
		'view' : 'sportsrec:club_add',
		'submit' : 'Add'
	}
	
	if request.method == "POST":
		form = ClubForm(request.POST)
		if form.is_valid():
			club = form.save()
			owner = Membership.objects.create(member=form.cleaned_data['owner'],club=club)
			contact = Membership.objects.create(member=form.cleaned_data['contact'],club=club)
			messages.add_message(request, messages.INFO, \
								 "Club successfully created!")
			return redirect('sportsrec:index')
	else:
		form = ClubForm()

	context['form'] = form

	return render(request, 'sportsrec/add_edit.html', context)

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).\
               dispatch(request, *args, **kwargs)

class UserMemberView(LoginRequiredMixin, generic.ListView):
    template_name = 'sportsrec/user_members.html'
    context_object_name = 'user_members'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['admin'] = is_admin(self.request.user)
        return context

    def get_queryset(self):
        if is_admin(self.request.user):
            return Member.objects.all()
        return Member.objects.filter(owner=self.request.user)

class TotalStats(generic.TemplateView):
    def get_user_stats(self, stats):
        #needed at all? performance? urgh
        if not self.request.user.is_authenticated():
            return

        try:
            meta = UserMeta.objects.get(user=self.request.user)
        except UserMeta.DoesNotExist:
            stats['user_member_count'] = 0
            stats['user_membership_count'] = 0
            stats['user_club_count'] = 0
        else:
            stats['user_member_count'] = meta.member_count
            stats['user_membership_count'] = meta.membership_count
            stats['user_club_count'] = meta.club_count

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TotalStats, self).get_context_data(**kwargs)

        stats = {}
        self.get_user_stats(stats)
        # Add in a QuerySet of all the books
        context['stats'] = stats
        return context
    

class Index(TotalStats):
    template_name='sportsrec/index.html'
    context_object_name='index'


class ClubList(generic.ListView):
    template_name = 'sportsrec/club_list.html'
    context_object_name = 'club_list'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['admin'] = is_admin(self.request.user)
        return context

    def get_queryset(self):
        return Club.objects.all()

def club_detail(request, pk):
	instance = Club.objects.get(pk=pk)
	context = {'club' : instance}
	
	return render(request, 'sportsrec/club_detail.html', context)
