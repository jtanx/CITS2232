from django.views import generic
from django.views.generic import *
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
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.db.models import Q

'''Mixins'''

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).\
               dispatch(request, *args, **kwargs)
               
class AdminMixin(object):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AdminMixin, self).get_context_data(**kwargs)
        context['admin'] = is_admin(self.request.user)
        return context
               
class MessageMixin(object):
    ''' Modification of class found at: http://goo.gl/aKvuWY'''
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            return super(MessageMixin, self).get(request, *args, **kwargs)
        except Http404:
            if self.error_message:
                messages.error(self.request, self.error_message)
            if self.error_url:
                return redirect(self.error_url)
            pass
        
    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)

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
        
class MemberAddView(LoginRequiredMixin, MessageMixin, FormView):
    template_name = 'sportsrec/add_edit.html'
    form_class = MemberForm
    success_message = 'Member created successfully!'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['created'] = True
        context['name'] = 'member'
        context['submit'] = 'Add'
        return context
    
    def form_valid(self, form):
        member = form.save
        #Don't save yet
        member = form.save(commit=False)
        #Tack on the owner
        member.owner = self.request.user
        member.save()
        self.success_url = reverse_lazy('sportsrec:member_detail',\
                                        kwargs = {'pk' : member.id, })
        return super(MemberAddView,self).form_valid(form)          
            
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
            member = form.save()
            #Regenerate form
            form = MemberForm(instance = member)
            context['pass'] = "Updated successfully!"
    else:
        form = MemberForm(instance = member)

    context['form'] = form

    return render(request, 'sportsrec/add_edit.html', context)

class MemberDetailView(MessageMixin, AdminMixin, DetailView):
    model = Member
    template_name='sportsrec/member_detail.html'
    error_message="That member doesn't exist"
    error_url=reverse_lazy('sportsrec:member_list')

    
class MemberDeleteView(LoginRequiredMixin, MessageMixin, DeleteView):
    model = Member
    success_url = reverse_lazy('sportsrec:member_list')
    template_name='sportsrec/member_delete.html'
    success_message='The member was deleted successfully.'
    error_message="You can't delete a member you didn't make."
    error_url=success_url
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['owned_clubs'] = Club.objects.filter(pk=self.kwargs['pk'])
        context['memberships'] = Membership.objects.filter(pk=self.kwargs['pk'])
        return context
    
    def get_queryset(self):
        qs = super(MemberDeleteView, self).get_queryset()
        if is_admin(self.request.user):
            return qs
        return qs.filter(owner=self.request.user)

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
        members = Member.objects.all()
        if not members.exists():
            messages.add_message(request, messages.ERROR, \
                    "You must create a member before adding a club.")
            return redirect('sportsrec:member_add')
    
    if request.method == "POST":
        form = ClubForm(request.POST, members=members)
        if form.is_valid():
            club = form.save()
            owner = Membership.objects.create(member=form.cleaned_data['owner'],club=club)
            owner.save()
            if form.cleaned_data['contact']:
                contact = form.cleaned_data['contact']
                if not Membership.objects.filter(member=contact, club=club).exists():
                    contact = Membership.objects.create(member=contact,club=club)
                    contact.save()
            messages.add_message(request, messages.INFO, \
                                 "Club successfully created!")
            return redirect('sportsrec:user_club_list')
    else:
        form = ClubForm(members=members)

    context['form'] = form

    return render(request, 'sportsrec/club_add_edit.html', context)

@login_required
def club_edit(request, pk):
    club = Club.objects.filter(pk=pk)
    if not club.exists():
        messages.add_message(request, messages.ERROR, \
                             "Club does not exist.")
        return redirect('sportsrec:club_list')

    club = club[0]
    if not is_admin(request.user) and not club.owner.owner == request.user:
        messages.add_message(request, messages.ERROR, \
                             "You cannot edit a club you did not make.")
        return redirect('sportsrec:club_list')

    #restrict to current members of club
    memberids = Membership.objects.filter(club=club)\
                    .values_list('member__pk', flat=True)
    members = Member.objects.filter(pk=memberids)

    context = {
            'created' : False, 'name' : 'club details',
            'view' : 'sportsrec:club_edit',
            'detail_view' : 'sportsrec:club_detail',
            'delete_view' : 'sportsrec:club_delete',
            'delete_text' : 'this club',
            'pk' : pk,
            'submit' : 'Edit'
    }
    
    if request.method == "POST":
        form = ClubForm(request.POST, members=members, instance=club)
        if form.is_valid():
            club = form.save()
            #Regenerate form
            form = ClubForm(members=members, instance=club)
            context['pass'] = 'Club details successfully edited!'
    else:
            form = ClubForm(members=members, instance=club)

    context['form'] = form

    return render(request, 'sportsrec/club_add_edit.html', context)

class ClubMembersView(MessageMixin, AdminMixin, ListView):
    template_name = 'sportsrec/club_member_list.html'
    context_object_name = 'club_member_list'
    paginate_by = 15 #15 members per page
    error_message = 'Club does not exist.'
    error_url = reverse_lazy('sportsrec:club_list')
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        try:
            club = Club.objects.get(pk=self.kwargs['pk'])
        except Club.DoesNotExist:
            raise Http404
        context['club'] = club
        return context
    
    def get_queryset(self):
        return Membership.objects.filter(club__id=self.kwargs['pk'])
    
class ClubDeleteView(LoginRequiredMixin, MessageMixin, DeleteView):
    model = Club
    success_url = reverse_lazy('sportsrec:user_club_list')
    template_name='sportsrec/club_delete.html'
    success_message='The club was deleted successfully.'
    error_message="You can't delete a club you didn't make."
    error_url=success_url
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['memberships'] = Membership.objects.filter(club__pk=self.kwargs['pk'])
        return context
    
    def get_queryset(self):
        qs = super(ClubDeleteView, self).get_queryset()
        if is_admin(self.request.user):
            return qs
        return qs.filter(owner__owner=self.request.user)    
             
class MemberList(LoginRequiredMixin, AdminMixin, ListView):
    template_name = 'sportsrec/member_list.html'
    context_object_name = 'members'
    paginate_by = 15 #15 members per page

    def get_queryset(self):
        if is_admin(self.request.user):
            return Member.objects.all()
        return Member.objects.filter(owner=self.request.user)

class MembershipApplyView(LoginRequiredMixin, MessageMixin, FormView):
    template_name = 'sportsrec/membership_apply.html'
    form_class = MembershipApplicationForm
    success_message = 'Membership application created successfully!'
    
    '''def get(self, request, *args, **kwargs):
        self.error_url = reverse_lazy('sportsrec:club_detail', \
                        kwargs = {'pk' : self.kwargs['pk']})
        return super(MembershipApplyView, self).get(request, *args, **kwargs)
    '''
    
    def get_form_kwargs(self):
        kwargs = super(MembershipApplyView, self).get_form_kwargs()
        members = Member.objects.filter(owner=self.request.user)
        existing_membership = Membership.objects.filter(club__id=self.kwargs['pk']).\
                    values_list('member__id', flat=True)
        existing_application = MembershipApplication.objects.filter(\
                        club__id=self.kwargs['pk']).\
                    values_list('member__id', flat=True)
        members = members.exclude(id__in=existing_membership)
        members = members.exclude(id__in=existing_application)
        if not members.exists():
            self.error_message = "You don't have any members that can apply to this club."
            self.error_url = reverse_lazy('sportsrec:club_detail', \
                        kwargs = {'pk' : self.kwargs['pk']})
            raise Http404
        
        kwargs['members'] = members
        return kwargs
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        try:
            club = Club.objects.get(pk=self.kwargs['pk'])
        except Club.DoesNotExist:
           self.error_message = "This club doesn't exist."
           self.error_url = reverse_lazy('sportsrec:club_list')
           raise Http404
           
        if not club.recruiting:
           self.error_message = "This club is not recruiting members."
           self.error_url = reverse_lazy('sportsrec:club_detail', \
                        kwargs = {'pk' : self.kwargs['pk']})
           raise Http404
            
        context['club'] = club
        return context
    
    def form_valid(self, form):
        try:
            club = Club.objects.get(pk=self.kwargs['pk'])
        except Club.DoesNotExist:
           self.error_message = "This club doesn't exist."
           self.error_url = reverse_lazy('sportsrec:club_list')
           raise Http404
        
        #Don't save yet
        application = form.save(commit=False)
        application.club = club
        application.save()
        self.success_url = reverse_lazy('sportsrec:club_detail',\
                                        kwargs = {'pk' : self.kwargs['pk']})
        return super(MembershipApplyView,self).form_valid(form)       
    
class MembershipApplicationView(LoginRequiredMixin, AdminMixin, ListView):
    template_name = 'sportsrec/membership_application_list.html'
    context_object_name = 'membership_application_list'
    paginate_by = 15
    
    def get_queryset(self):
        if is_admin(self.request.user):
            return MembershipApplication.objects.all()
        return MembershipApplication.objects.filter(member__owner=self.request.user)
        
class MembershipApplicationDeleteView(LoginRequiredMixin, MessageMixin, AdminMixin, DeleteView):
    model = MembershipApplication
    success_url = reverse_lazy('sportsrec:membership_application_list')
    template_name='sportsrec/membership_application_delete.html'
    success_message='Your membership appplication was removed successfully.'
    error_message="You can't remove a membership application you didn't make."
    error_url=success_url

    def get_queryset(self):
        qs = super(MembershipApplicationDeleteView, self).get_queryset()
        if not is_admin(self.request.user):
            return qs.filter(member__owner=self.request.user)
        return qs
        
class MembershipList(LoginRequiredMixin, AdminMixin, ListView):
    template_name = 'sportsrec/membership_list.html'
    context_object_name = 'membership_list'
    paginate_by = 15 #15 members per page

    def get_queryset(self):
        if is_admin(self.request.user):
            return Membership.objects.all()
        return Membership.objects.filter(member__owner=self.request.user)

class MembershipDetailView(LoginRequiredMixin, MessageMixin, DetailView):
    model = Membership
    template_name='sportsrec/membership_detail.html'
    error_message="You don't administer that membership."
    error_url=reverse_lazy('sportsrec:membership_list')
    
    def get_queryset(self):
        qs = super(MembershipDetailView, self).get_queryset()
        if not is_admin(self.request.user):
            return qs.filter(member__owner=self.request.user)
        return qs
        
class MembershipDeleteView(LoginRequiredMixin, MessageMixin, DeleteView):
    model = Membership
    success_url = reverse_lazy('sportsrec:membership_list')
    template_name='sportsrec/membership_delete.html'
    success_message='Your membership was removed successfully.'
    error_message="You can't remove a membership you didn't make."
    error_url=success_url

    def get_queryset(self):
        qs = super(MembershipDeleteView, self).get_queryset()
        if not is_admin(self.request.user):
            return qs.filter(Q(member__owner=self.request.user) | Q(club__owner__owner=self.request.user))
        return qs
        
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


class ClubList(AdminMixin, ListView):
    template_name = 'sportsrec/club_list.html'
    context_object_name = 'club_list'
    paginate_by = 15 #15 clubs/page

    def get_queryset(self):
        return Club.objects.all()

class UserClubList(LoginRequiredMixin, AdminMixin, ListView):
    template_name = 'sportsrec/user_club_list.html'
    context_object_name = 'club_list'
    paginate_by = 15 #15 clubs/page

    def get_queryset(self):
        if is_admin(self.request.user):
            return Club.objects.all()
        members=Member.objects.filter(owner=self.request.user).values_list('pk', flat=True)
        return Club.objects.filter(owner__pk__in=members).order_by('id')

class UserClubApplicationList(LoginRequiredMixin, MessageMixin, AdminMixin, ListView):
    template_name = 'sportsrec/user_club_application_list.html'
    context_object_name = 'user_club_application_list'
    paginate_by = 15 #15 applications/page
    
    def post(self, request, *args, **kwargs):
        form = ApplicationForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['application_id']
            try:
                application = MembershipApplication.objects.get(id=id)
            except MembershipApplication.DoesNotExist:
                messages.error(self.request, 'Membership application does not exist')
                return redirect('sportsrec:user_club_application_list')
            
            if application.club.owner.owner != self.request.user and not is_admin(self.request.user):
                messages.error(self.request, 'You cannot modify this application')
                return redirect('sportsrec:user_club_application_list')
            
            if form.cleaned_data['accept']:
                membership = Membership.objects.create(club=application.club, member=application.member)
                try:
                    membership.save()
                except:
                    messages.error(self.request, 'Could not create membership')
                    return redirect('sportsrec:user_club_application_list')
                application.delete()
            else:
                application.rejected = True
                application.save()
            messages.success(self.request, 'Successfully actioned the application!') #laziness
        else:
            messages.error(self.request, "Invalid accept/reject post.")
        return redirect('sportsrec:user_club_application_list')

    def get_queryset(self):
        if is_admin(self.request.user):
            return MembershipApplication.objects.filter(rejected=False)
        clubs = Club.objects.filter(owner__owner=self.request.user).values_list('pk', flat=True)
        return MembershipApplication.objects.filter(club__id__in=clubs, rejected=False)
        
class ClubDetailView(AdminMixin, MessageMixin, DetailView):
    model = Club
    template_name='sportsrec/club_detail.html'
    error_message="This club doesn't exist."
    error_url=reverse_lazy('sportsrec:club_list')
    
def search(request):
	context = {}
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			club = Club.objects.get(name=name)
			if club:
				context['exists'] = True
				context['club'] = club
			else:
				context['exists'] = False
	else:
		form = SearchForm()
		
	context['form'] = form
	return render(request, 'sportsrec/search.html', context)
