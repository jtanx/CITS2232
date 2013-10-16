from django.forms import Form, ModelForm, Textarea
from django import forms
from django.forms import extras
from django.contrib.auth.models import User
from sportsrec.models import *
from django.contrib.auth import authenticate
import re, decimal


class SocialCleanerMixin(object):
    grep = re.compile(r"(?i)^(?:https?://.*/)?([a-zA-Z0-9-\._@'t#]*)")
    def clean(self):
        cleaned_data = super(SocialCleanerMixin, self).clean()
        facebook = cleaned_data.get("facebook")
        twitter = cleaned_data.get("twitter")
        if facebook:
            m = re.match(self.grep, facebook)
            facebook = None
            if m:
                facebook = m.group(1)
            cleaned_data['facebook'] = facebook
        if twitter:
            m = re.match(self.grep, twitter)
            twitter = None
            if m:
                twitter = m.group(1)
            cleaned_data['twitter'] = twitter
            
        return cleaned_data

class LoginForm(Form):
    '''A login form'''
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    next_location = forms.CharField(required=False, widget=forms.HiddenInput)
    
class RegistrationForm(Form):
    '''A registration form'''
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)

    def clean_username(self):
        '''Username validation'''
        username = self.cleaned_data.get("username")
        if username:
            msg = None
            if len(username) < 4:
                msg = "Usernames must be at least 4 characters long."
            elif not re.match(r'^[a-zA-Z0-9]+.*[a-zA-Z0-9]', username):
                msg = "Usernames must begin and end with " +\
                      "an alphanumeric character."
            elif not re.match(r'^[a-zA-Z0-9-_.]+$', username):
                msg = "Usernames must be composed of the characters " + \
                      "A-Z, a-z or any of -_."
            elif User.objects.filter(username=username).exists():
                msg = "That username is already in use."
            if msg:
                self._errors["username"] = self.error_class([msg])
                del self.cleaned_data["username"]
        
        return username #always return

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            msg = "That email is already in use."
            self._errors["email"] = self.error_class([msg])
            del self.cleaned_data["email"]
        return email
    
    def clean(self):
        '''Form validation'''
        cleaned_data = super(RegistrationForm, self).clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")

        if p1 and p2:
            msg = None
            if p1 != p2:
                msg="Passwords do not match."
            elif len(p1) < 6:
                msg = "Password must be at least 6 characters long."

            if msg:
                self._errors["confirm_password"] = self.error_class([msg])
                del cleaned_data["password"]
                del cleaned_data["confirm_password"]
        return cleaned_data


class UserProfileForm(Form):
    current_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    
    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        super(UserProfileForm, self).__init__(*args, **kwargs)

        self.fields['email'].initial = instance.email
        self.fields['first_name'].initial = instance.first_name
        self.fields['last_name'].initial = instance.last_name

    def clean_current_password(self):
        password = self.cleaned_data.get("current_password")
        msg = None
        
        if password:
            user = authenticate(username=self.instance.username,
                                password=password)
            if user is None or not user.is_active:
                msg = "Incorrect password"
                self._errors["current_password"] = self.error_class([msg])
                del self.cleaned_data["current_password"]
        return password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).\
                     exclude(pk=self.instance.pk).exists():
            
            msg = "That email is already in use."
            self._errors["email"] = self.error_class([msg])
            del self.cleaned_data["email"]
        return email
    
    def clean(self):
        '''Form validation'''
        cleaned_data = super(UserProfileForm, self).clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")

        if p1 and p2:
            msg = None
            if p1 != p2:
                msg="Passwords do not match."
            elif len(p1) < 6:
                msg = "Password must be at least 6 chars long."

            if msg:
                self._errors["confirm_password"] = self.error_class([msg])
                del cleaned_data["new_password"]
                del cleaned_data["confirm_password"]
        return cleaned_data

class MemberForm(SocialCleanerMixin, ModelForm):    
    class Meta:
        model=Member
        fields=['first_name', 'last_name', 'email', 'address',
                'facebook', 'twitter', 'phone','interests']
        widgets = {
            'interests': Textarea(attrs={
                'cols': 70, 'rows': 6,
                'style' : 'width: 100%',
                'maxlength' :  Member._meta.get_field('interests').max_length}),
        }

class MembershipApplicationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        members = kwargs.pop('members')
        super(MembershipApplicationForm, self).__init__(*args, **kwargs)
        self.fields['member'].queryset = members
 
    class Meta:
        model=MembershipApplication
        fields=['member']
        
class MembershipPaidForm(ModelForm):    
    class Meta:
        model=Membership
        fields=['last_paid']
        widgets = {
            'last_paid' : extras.SelectDateWidget()
        }
        
class ApplicationForm(Form):
    application_id = forms.IntegerField(widget=forms.HiddenInput())
    accept = forms.IntegerField(widget=forms.HiddenInput())
    
class ClubForm(SocialCleanerMixin, ModelForm):
    '''Club add/edit form. Requires member queryset.'''
    location = forms.CharField(max_length=40, required=False)
    search_tags = forms.CharField(max_length=250, required=False)
    grep = re.compile('\s*[a-zA-Z0-9-]+\s*')
    
    def __init__(self, *args, **kwargs):
        member_queryset = kwargs.pop('members')
        super(ClubForm, self).__init__(*args, **kwargs)
        self.fields['owner'].queryset = member_queryset
        self.fields['owner'].required = True
        self.fields['contact'].queryset = member_queryset
        if self.instance.latitude and self.instance.longitude:
            self.fields['location'].initial = \
                "%s, %s" % (self.instance.latitude, self.instance.longitude)
        try:
            self.fields['search_tags'].initial = ", ".join(str(tag) for tag in self.instance.tags.all())
        except ValueError:
            pass
    
    def save(self, *args, **kwargs):
        if 'latitude' in self.cleaned_data:
            self.instance.latitude = self.cleaned_data['latitude']
            self.instance.longitude = self.cleaned_data['longitude']
        stags = self.cleaned_data.get('search_tags')
        super(ClubForm, self).save(*args, **kwargs)
        
        if stags:
            self.instance.tags.clear()
            for stag in stags:
                if len(stag) > 0:
                    tag, created = ClubTag.objects.get_or_create(name=stag)
                    self.instance.tags.add(tag)
            
        return super(ClubForm, self).save(*args, **kwargs)
        
    def clean_search_tags(self):
        stags = self.cleaned_data.get("search_tags")
        if stags:
            sep = re.split(r',|\s', stags)
            cleaned = [x.strip() for x in sep if re.match(self.grep, x)]
            return cleaned
        return stags
        
    def clean(self):
        cleaned_data = super(ClubForm, self).clean()
        location = cleaned_data.get("location")
        ok = True
        if location:
            parts = location.split(',')
            if len(parts) != 2:
                ok = False
            else:
                try:
                    lat = decimal.Decimal(parts[0])
                    long = decimal.Decimal(parts[1])
                except:
                    ok = False
                else:
                    cleaned_data['latitude'] = lat
                    cleaned_data['longitude'] = long
        if not ok:
            msg = "Location must be in the form latitude, longitude in decimal notation."
            self._errors["location"] = self.error_class([msg])
            del cleaned_data['location']
        return cleaned_data
        
    class Meta:
            model=Club
            fields=['name','owner','address','location','search_tags','type','recruiting','contact',
                            'facebook','twitter','description']
            widgets = {
                'description': Textarea(attrs={
                    'cols': 70, 'rows': 6,
                    'style' : 'width: 100%',
                    'maxlength' :  Club._meta.get_field('description').max_length})
            }
    
class SearchForm(Form):
	name = forms.CharField()
