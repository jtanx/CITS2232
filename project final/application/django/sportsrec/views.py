from django.views.generic import *
from sportsrec.models import *
from sportsrec.forms import *
from django.shortcuts import redirect,render
from django.http import *
from django.contrib.auth import authenticate, login, logout
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
    '''Forces login for a specified view'''
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).\
               dispatch(request, *args, **kwargs)

class AdminRequiredMixin(object):
    '''Views only for admins'''
    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            return redirect('sportsrec:index')
        return super(AdminRequiredMixin, self).\
               dispatch(request, *args, **kwargs)


class AdminMixin(object):
    '''Sets context variable telling if current user is admin or not'''
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
            raise Http404

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)

def login_user(request):
    '''Logs in the user, based on provided credentials'''
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
    '''Logs out the user'''
    logout(request)
    return redirect('sportsrec:index')

def register(request):
    '''User registration form'''
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
    '''User profile modification form'''
    context = {
        'created' : False, 'name' : 'user profile',
        'view' : 'sportsrec:user_profile',
        'submit' : 'Submit', 'user_profile' : True,
        'admin' : is_admin(request.user),
        'user_profile' : True
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

class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    '''Only for admins - details about a user'''
    model = User
    template_name='sportsrec/user_detail.html'
    error_message="That user doesn't exist"
    error_url=reverse_lazy('sportsrec:index')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        user = User.objects.get(pk=self.kwargs['pk'])
        context['user_not_admin'] = not is_admin(user)
        context['owned_members'] = Member.objects.filter(owner=user)
        context['owned_clubs'] = Club.objects.filter(owner__owner=user)

        return context

class UserPromoteView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    '''Only for admins - promote a user to admin status'''
    model = User
    template_name='sportsrec/user_confirm.html'
    error_message="That user doesn't exist"
    error_url=reverse_lazy('sportsrec:index')
    success_message = 'Membership application created successfully!'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['promote'] = True

        return context

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])
        if is_admin(user):
            messages.error(self.request, 'User is already an admin')
            url = reverse_lazy('sportsrec:user_detail',\
                                        kwargs = {'pk' : user.id, })
            return redirect(url)
        group = Group.objects.get(name="End Admin")
        user.groups.add(group)
        user.save()
        messages.success(self.request, self.success_message)
        url = reverse_lazy('sportsrec:user_detail',\
                                        kwargs = {'pk' : user.id, })
        return redirect(url)

class UserDemoteView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    '''Only for an admin - demote yourself'''
    template_name='sportsrec/user_confirm.html'
    context_object_name='demote'

    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])
        if not self.request.user.is_superuser and not user==self.request.user:
            messages.error(self.request, 'You can only demote yourself')
            return redirect('sportsrec:index')
        elif not is_admin(user):
            messages.error(self.request, 'Nothing to demote - not an admin.')
            return redirect('sportsrec:index')

        return super(self.__class__, self).\
               dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])
        if user.is_superuser:
            messages.error(self.request, 'Nice try')
            return redirect('sportsrec:index')
        group = Group.objects.get(name="End Admin")
        user.groups.remove(group)
        user.save()
        messages.success(self.request, "%s was demoted." % user)
        return redirect('sportsrec:index')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        user = User.objects.get(pk=self.kwargs['pk'])
        context['demote_user'] = user
        context['demote'] = True
        return context

class UserDisableView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    '''Only for admin - disable a user'''
    model = User
    success_url = reverse_lazy('sportsrec:index')
    template_name='sportsrec/user_confirm.html'
    success_message='The user was disabled successfully.'
    error_message="That user doesn't exist."
    error_url=success_url

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['disable'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])
        if not request.user.is_superuser and is_admin(user):
            messages.error(self.request, 'Cannot disable an admin user and not superuser')
            return redirect('sportsrec:index')
        return super(UserDisableView, self).\
               dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])
        if not request.user.is_superuser and is_admin(user):
            messages.error(self.request, 'User is already an admin')
            url = reverse_lazy('sportsrec:user_detail',\
                                        kwargs = {'pk' : user.id, })
            return redirect(url)
        user.is_active = False
        user.save()
        messages.success(self.request, self.success_message)
        url = reverse_lazy('sportsrec:user_detail',\
                                        kwargs = {'pk' : user.id, })
        return redirect(url)

class UserEnableView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    '''Only for admin - enable a user'''
    model = User
    success_url = reverse_lazy('sportsrec:index')
    template_name='sportsrec/user_confirm.html'
    success_message='The user was enabled successfully.'
    error_message="That user doesn't exist."
    error_url=success_url

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['enable'] = True
        return context

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs['pk'])
        user.is_active = True
        user.save()
        messages.success(self.request, self.success_message)
        url = reverse_lazy('sportsrec:user_detail',\
                                        kwargs = {'pk' : user.id, })
        return redirect(url)

class UserListView(LoginRequiredMixin, AdminRequiredMixin, AdminMixin, ListView):
    '''Only for admin - a list of users'''
    template_name = 'sportsrec/user_list.html'
    context_object_name = 'users'
    paginate_by = 15 #15 members per page

    def get_queryset(self):
        return User.objects.all().order_by('is_active', 'id')

class MemberAddView(LoginRequiredMixin, MessageMixin, FormView):
    '''View to add members to the site'''
    template_name = 'sportsrec/add_edit.html'
    form_class = MemberForm
    success_message = 'Member created successfully!'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['member_add'] = True
        context['created'] = True
        context['name'] = 'member'
        context['submit'] = 'Add'
        return context

    def form_valid(self, form):
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
    '''Edit member details view'''
    member = Member.objects.filter(pk=pk)
    if not member.exists():
        messages.add_message(request, messages.ERROR, \
                             "Member does not exist.")
        return redirect('sportsrec:members')

    member = member[0]

    if not is_admin(request.user) and not member.owner == request.user:
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
        'submit' : 'Edit',
        'member_edit' : True
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
    '''Member detail view'''
    model = Member
    template_name='sportsrec/member_detail.html'
    error_message="That member doesn't exist"
    error_url=reverse_lazy('sportsrec:member_list')


class MemberDeleteView(LoginRequiredMixin, MessageMixin, DeleteView):
    '''Delete a member (only admin or user owning admin'''
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
    '''Add a club'''
    context = {
        'created' : True, 'name' : 'club',
        'view' : 'sportsrec:club_add',
        'submit' : 'Add',
        'club_add' : True
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
    '''edit club details'''
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
    members = Member.objects.filter(pk__in=memberids)

    context = {
            'created' : False, 'name' : 'club details',
            'view' : 'sportsrec:club_edit',
            'detail_view' : 'sportsrec:club_detail',
            'delete_view' : 'sportsrec:club_delete',
            'delete_text' : 'this club',
            'pk' : pk,
            'submit' : 'Edit',
            'club_edit' : True
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
    '''List of members for a club'''
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
    '''Delete a club. Only for admin or owner of club'''
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
    '''List of members owned by the logged-in user'''
    template_name = 'sportsrec/member_list.html'
    context_object_name = 'members'
    paginate_by = 15 #15 members per page

    def get_queryset(self):
        if is_admin(self.request.user):
            return Member.objects.all()
        return Member.objects.filter(owner=self.request.user)

class MembershipApplyView(LoginRequiredMixin, MessageMixin, FormView):
    '''Club membership application form'''
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
    '''See all membership applications for this user'''
    template_name = 'sportsrec/membership_application_list.html'
    context_object_name = 'membership_application_list'
    paginate_by = 15

    def get_queryset(self):
        if is_admin(self.request.user):
            return MembershipApplication.objects.all()
        return MembershipApplication.objects.filter(member__owner=self.request.user)

class MembershipApplicationDeleteView(LoginRequiredMixin, MessageMixin, AdminMixin, DeleteView):
    '''Delete a membership application'''
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
    '''See all memberships for this owner'''
    template_name = 'sportsrec/membership_list.html'
    context_object_name = 'membership_list'
    paginate_by = 15 #15 members per page

    def get_queryset(self):
        if is_admin(self.request.user):
            return Membership.objects.all()
        return Membership.objects.filter(member__owner=self.request.user)

class MembershipDetailView(LoginRequiredMixin, MessageMixin, AdminMixin, DetailView):
    '''See the details of a membership'''
    model = Membership
    template_name='sportsrec/membership_detail.html'
    error_message="You don't administer that membership."
    error_url=reverse_lazy('sportsrec:membership_list')

    def get_queryset(self):
        qs = super(MembershipDetailView, self).get_queryset()
        if not is_admin(self.request.user):
            return qs.filter(Q(member__owner=self.request.user) | Q(club__owner__owner=self.request.user))
        return qs

class MembershipUpdateView(LoginRequiredMixin, MessageMixin, FormView):
    '''Set the last paid date for a membership (admin and club owner only)'''
    form_class=MembershipPaidForm
    template_name = 'sportsrec/membership_update.html'
    success_message='Successfully set the last paid date'
    error_message="You can't update a membership you didn't create."
    error_url=reverse_lazy('sportsrec:index')
    
    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        if not is_admin(self.request.user):
            membership = Membership.objects.filter(pk=self.kwargs['pk'], \
                            club__owner__owner=self.request.user)
        else:
            membership = Membership.objects.filter(pk=self.kwargs['pk'])
        if not membership.exists():
            raise Http404
            
        self.instance = membership[0]
        kwargs['instance'] = membership[0]
        return kwargs
    
    def form_valid(self, form):
        
        self.success_url=reverse_lazy('sportsrec:membership_detail',\
                                      kwargs = {'pk' : self.kwargs['pk'], })
        form.save()
        return super(self.__class__, self).form_valid(form)

    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['membership'] = self.instance
        return context
        
class MembershipDeleteView(LoginRequiredMixin, MessageMixin, DeleteView):
    '''Delete a membership (member or club owner or admin only)'''
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

class StatsOverView(TemplateView):
    '''Stats view'''
    template_name='sportsrec/statistics.html'
    context_object_name='stats'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        admin = Group.objects.get(name="End Admin")
        context['user_count'] = User.objects.all().count()
        context['admin_count'] = User.objects.filter(groups=admin).count()
        context['member_count'] = Member.objects.all().count()
        context['club_count'] = Club.objects.all().count()
        context['application_count'] = MembershipApplication.objects.all().count()
        return context

class ClubTypeStatsView(ListView):
    '''Stats for clubs/type'''
    template_name = 'sportsrec/statistics_clubs.html'
    context_object_name = 'clubtypes'
    paginate_by = 15 #15 club types per page

    def get_queryset(self):
        return ClubType.objects.all().order_by('-club_count','name')

class Index(AdminMixin, TemplateView):
    '''The main index view. Shows ownerless clubs for admins'''
    template_name='sportsrec/index.html'
    context_object_name='index'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(Index, self).get_context_data(**kwargs)
        if is_admin(self.request.user):
            ownerless = Club.objects.filter(owner=None)
            context['ownerless'] = ownerless
        return context


class ClubList(AdminMixin, ListView):
    '''Full club listing'''
    template_name = 'sportsrec/club_list.html'
    context_object_name = 'club_list'
    paginate_by = 15 #15 clubs/page

    def get_queryset(self):
        return Club.objects.all()

class UserClubList(LoginRequiredMixin, AdminMixin, ListView):
    '''Club listing for a given user'''
    template_name = 'sportsrec/user_club_list.html'
    context_object_name = 'club_list'
    paginate_by = 15 #15 clubs/page

    def get_queryset(self):
        if is_admin(self.request.user):
            return Club.objects.all()
        members=Member.objects.filter(owner=self.request.user).values_list('pk', flat=True)
        return Club.objects.filter(owner__pk__in=members).order_by('id')

class UserClubApplicationList(LoginRequiredMixin, MessageMixin, AdminMixin, ListView):
    '''Membership application list for a given user'''
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

            if not is_admin(self.request.user) and application.club.owner.owner != self.request.user:
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
    '''Details of a club'''
    model = Club
    template_name='sportsrec/club_detail.html'
    error_message="This club doesn't exist."
    error_url=reverse_lazy('sportsrec:club_list')


def search(request):
    '''Main search form'''
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


class SearchNameView(MessageMixin, ListView):
    '''Search by club name view'''
    template_name = 'sportsrec/search_name.html'
    context_object_name = 'search_name'
    paginate_by = 15 #15 clubs/page

    def get_queryset(self):
        if 'query' in self.request.GET:
            query = self.request.GET['query']
            return Club.objects.filter(name__icontains=query)
        return Club.objects.none()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '')
        return context

class SearchTagView(MessageMixin, ListView):
    '''Search by club tags and club type view'''
    template_name = 'sportsrec/search_tag.html'
    context_object_name = 'search_tag'
    paginate_by = 15 #15 clubs/page

    def get_queryset(self):
        if 'query' in self.request.GET:
            query = self.request.GET['query']
            tag = Club.objects.filter(tags__name__iexact=query)
            ctype = Club.objects.filter(type__name__iexact=query)
            return (tag | ctype).distinct()
        return Club.objects.none()
        
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '')
        return context
        
class SearchLocationView(MessageMixin, ListView):
    '''Search by location (geocoding) view'''
    template_name = 'sportsrec/search_location.html'
    context_object_name = 'search_location'
    paginate_by = 15 #15 clubs/page

    #only uses first result from google api
    def geocode(self, address):
        result = None
        url = 'http://maps.googleapis.com/maps/api/geocode/json'
        params = urllib.urlencode({'address' : address, 'sensor' : 'false', 'region': 'AU'})
        url = url + '?' + params
        response = urllib2.urlopen(url)
        try:
            vals = json.load(response)
        except ValueError:
            return result

        if 'results' in vals and len(vals['results']) > 0:
            loc = vals['results'][0]['geometry']['location']
            result = (loc['lat'], loc['lng'])
        return result

    def parse_latlng(self, query):
        parts = query.split(',')
        if len(parts) != 2:
            return None
        try:
            lat = float(parts[0])
            long = float(parts[1])
        except:
            return None
        return (lat, long)
        
    def get_queryset(self):
        if 'query' in self.request.GET:
            location = self.request.GET['query']
            #Don't geocode if it's already in the right format.
            latlng = self.parse_latlng(location)
            if latlng is None:
                latlng = self.geocode(location)

            if latlng:
                self.centre = latlng
                self.radius = radius = 5
                if 'radius' in self.request.GET:
                    try:
                        radius = int(self.request.GET['radius'])
                    except ValueError:
                        pass
                    self.radius = radius
                nearby = Club.location.nearby_locations(latlng[0], latlng[1], radius)
                return nearby
        return Club.objects.none()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '')
        context['centre'] = self.centre
        context['radius'] = self.radius
        return context
