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

def member_detail(request, pk):
    try:
        member = Member.objects.get(pk=pk)
    except Member.DoesNotExist:
        messages.add_message(request, messages.ERROR, \
                            "Member with that id does not exist.")
        return redirect('sportsrec:index')

    owned_clubs = Club.objects.filter(owner=member)
    context = {'member' : member, 'owned_clubs' : owned_clubs}
    return render(request, 'sportsrec/member_detail.html', context)

@login_required
def member_add(request):
    context = {
        'created' : True, 'name' : 'member',
        'view' : 'sportsrec:member_add',
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
            return redirect('sportsrec:members')
    else:
        form = MemberForm()

    context['form'] = form

    return render(request, 'sportsrec/add_edit.html', context)
            

@login_required
def member_edit(request, pk):
    member = Member.objects.filter(pk=pk)
    if not member.exists():
        messages.add_message(request, messages.ERROR, \
                             "Member does not exist.")
        return redirect('sportsrec:members')

    member = member[0]
    
    if not member.owner == request.user and not is_admin(request.user):
        messages.add_message(request, messages.ERROR, \
                             "You can't edit a member you didn't create.")
        return redirect('sportsrec:members')

    context = {
        'created' : False,
        'name' : 'member details',
        'view' : 'sportsrec:member_edit',
        'detail_view' : 'sportsrec:member_detail',
        'delete_view' : 'sportsrec:member_delete',
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
def member_delete(request, pk):
    member = Member.objects.filter(pk=pk)
    if not member.exists():
        messages.add_message(request, messages.ERROR, \
                             "Member does not exist.")
        return redirect('sportsrec:members')

    member = member[0]
    
    if not member.owner == request.user and not is_admin(request.user):
        messages.add_message(request, messages.ERROR, \
                             "You can't delete a member you didn't create.")
        return redirect('sportsrec:members')
    
    context = {
        'name' : "member: '%s'" % member,
        'view' : 'sportsrec:member_delete',
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
        return redirect('sportsrec:members')
    
    return render(request, 'sportsrec/delete.html', context)

@login_required
def club_add(request):
	context = {
		'created' : True, 'name' : 'club',
		'view' : 'sportsrec:club_add',
		'submit' : 'Add'
	}

        if not is_admin(request.user):
            members = Member.objects.filter(owner=request.user)
            if not members.exists():
                messages.add_message(request, messages.ERROR, \
                             "You must create a member before adding a club.")
                return redirect('sportsrec:member_add')
        else:
            members=  Member.objects.all()
	
	if request.method == "POST":
		form = ClubForm(request.POST, members=members)
		if form.is_valid():
			club = form.save()
			owner = Membership.objects.create(member=form.cleaned_data['owner'],club=club)
			owner.save()
			if form.cleaned_data['contact']:
				contact = Membership.objects.create(member=form.cleaned_data['contact'],club=club)
				contact.save()
			messages.add_message(request, messages.INFO, \
								 "Club successfully created!")
			return redirect('sportsrec:index')
	else:
		form = ClubForm(members=members)

	context['form'] = form

	return render(request, 'sportsrec/add_edit.html', context)

@login_required
def club_edit(request, pk):
    club = Club.objects.filter(pk=pk)
    if not club.exists():
        messages.add_message(request, messages.ERROR, \
                             "Club does not exist.")
        return redirect('sportsrec:club_list')

    club = club[0]
    if not club.owner.owner == request.user and not is_admin(request.user):
        messages.add_message(request, messages.ERROR, \
                             "You cannot edit a club you did not make.")
        return redirect('sportsrec:club_list')

    #restrict to current members of club
    memberids = Membership.objects.values_list('pk', flat=True).\
                filter(club=club)
    members = Member.objects.filter(pk__in=set(memberids))

    context = {
            'created' : False, 'name' : 'club details',
            'view' : 'sportsrec:club_edit',
            'detail_view' : 'sportsrec:club_detail',
            'pk' : pk,
            'submit' : 'Edit'
    }
    
    if request.method == "POST":
        form = ClubForm(request.POST, members=members, instance=club)
        if form.is_valid():
            club = form.save()
            context['pass'] = 'Club details successfully edited!'
    else:
            form = ClubForm(members=members, instance=club)

    context['form'] = form

    return render(request, 'sportsrec/add_edit.html', context)

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).\
               dispatch(request, *args, **kwargs)

class MemberList(LoginRequiredMixin, generic.ListView):
    template_name = 'sportsrec/member_list.html'
    context_object_name = 'members'
    paginate_by = 15 #15 members per page

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['admin'] = is_admin(self.request.user)
        return context

    def get_queryset(self):
        if is_admin(self.request.user):
            return Member.objects.all()
        return Member.objects.filter(owner=self.request.user)

class MembershipList(LoginRequiredMixin, generic.ListView):
    template_name = 'sportsrec/membership_list.html'
    context_object_name = 'membership_list'
    paginate_by = 15 #15 members per page

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['admin'] = is_admin(self.request.user)
        return context

    def get_queryset(self):
        if is_admin(self.request.user):
            return Membership.objects.all()
        return Membership.objects.filter(member__owner=self.request.user)

def membership_detail(request, pk):
    try:
        membership = Membership.objects.get(pk=pk)
    except Membership.DoesNotExist:
        messages.add_message(request, messages.ERROR, \
                             "Membership does not exist.")
        return redirect('sportsrec:index')

    if membership.member.owner != request.user and not is_admin(request.user):
        messages.add_message(request, messages.ERROR, \
                             "You cannot edit a membership you do not own.")
        return redirect('sportsrec:index')

    context = {'membership' : membership}
    return render(request, 'sportsrec/membership_detail.html', context)

class TotalStats(generic.TemplateView):
    def get_user_stats(self, stats):
        #needed at all? performance? urgh
        if not self.request.user.is_authenticated():
            return

        try:
            meta = UserMeta.objects.get(user=self.request.user)
        except UserMeta.DoesNotExist:
            stats['member_count'] = 0
            stats['membership_count'] = 0
            stats['user_club_count'] = 0
        else:
            stats['member_count'] = meta.member_count
            stats['membership_count'] = meta.membership_count
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
    paginate_by = 15 #15 clubs/page

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['admin'] = is_admin(self.request.user)
        return context

    def get_queryset(self):
        return Club.objects.all()

class UserClubList(LoginRequiredMixin, generic.ListView):
    template_name = 'sportsrec/user_club_list.html'
    context_object_name = 'club_list'
    paginate_by = 15 #15 clubs/page

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['admin'] = is_admin(self.request.user)
        return context

    def get_queryset(self):
        members=  Member.objects.filter(owner=self.request.user)
        return Club.objects.filter(owner__in=members).order_by('id')

def club_detail(request, pk):
	instance = Club.objects.get(pk=pk)
	context = {'club' : instance}
	
	return render(request, 'sportsrec/club_detail.html', context)
