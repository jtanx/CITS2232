from django.forms import ModelForm
from django.contrib.auth.models import User
from sportsrec.models import SiteUser

class UserForm(ModelForm):
    class Meta:
        model = User

    
class SiteUserForm(ModelForm):
    class Meta:
        model = SiteUser
        exclude = ['user']
