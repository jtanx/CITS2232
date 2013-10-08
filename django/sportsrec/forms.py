from django.forms import Form, ModelForm
from django import forms
from django.contrib.auth.models import User
from sportsrec.models import *
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


class UserProfileForm(ModelForm):
    class Meta:
        model = Contact








