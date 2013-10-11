from django.forms import Form, ModelForm, Textarea
from django import forms
from django.contrib.auth.models import User
from sportsrec.models import *
from django.contrib.auth import authenticate
import re

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
                msg = "Password must be at least 6 chars long."

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

class MemberForm(ModelForm):    
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

class DeleteForm(Form):
    confirm = forms.BooleanField()
    
class ClubForm(ModelForm):
	class Meta:
		model=Club
		fields=['name','owner','address','location','tags','type','recruiting','contact',
				'facebook','twitter','description']
		widgets = {
            'description': Textarea(attrs={
                'cols': 70, 'rows': 6,
                'style' : 'width: 100%',
                'maxlength' :  Club._meta.get_field('description').max_length}),
        }
