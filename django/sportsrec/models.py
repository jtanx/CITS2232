from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from datetime import datetime


#Contact must be before User so the foreign key constraint is generated
class Contact(models.Model):
    '''Public contact details'''
    public_email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=40, blank=True, null=True)
    twitter = models.CharField(max_length=40, blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    fax = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        abstract = True
        
    def __unicode__(self):
        return '%s' % (self.public_email)


'''
class SiteUser(Contact):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return '%s <%s>' % (self.user.username)#, self.contact.public_email)

def create_site_user(sender, instance, created, **kwargs):
    #Each time a Django user is made, make the corresponding site user.
    if created:
        #contact = Contact.objects.create()
        profile = SiteUser.objects.create(user=instance)#, contact=contact)

post_save.connect(create_site_user, sender=User)
'''

class Member(Contact):
    lastname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    interests = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(User)
    
    def __unicode__(self):
        return '%s %s' % (self.firstname, self.lastname)

class Club(Contact):
    name = models.CharField(max_length=40, unique=True)
    type = models.CharField(max_length=40, blank=True, null=True)
    location = models.CharField(max_length=40, blank=True, null=True)
    membercount = models.IntegerField(default=0)
    created = models.DateField(default=datetime.now)
    recruiting = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(User)
    #contact = models.OneToOneField('Contact')
    
    def __unicode__(self):
        return '%s' % (self.name)

class Membership(models.Model):
    joined = models.DateField(default=datetime.now)
    lastpaid = models.DateField(blank=True, null=True)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')
	
    def __unicode__(self):
        return '%s belongs to %s' % (self.member, self.club)
	
	
