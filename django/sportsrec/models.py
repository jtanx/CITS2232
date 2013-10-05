from django.db import models
from django.contrib.auth.models import User

#Contact must be before User so the foreign key constraint is generated
class Contact(models.Model):
    '''Public contact details'''
    email = models.CharField(max_length=40)
    address = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=40, blank=True, null=True)
    twitter = models.CharField(max_length=40, blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    fax = models.CharField(max_length=40, blank=True, null=True)
	
    def __unicode__(self):
        '''
            #is this allowed? id is not defined above but it will be...
            "There's no way to tell what the value of an ID will be before you call save(), 
            because that value is calculated by your database, not by Django."

            http://stackoverflow.com/questions/14234917/django-how-to-get-self-id-when-saving-a-new-object
        '''
        return '%s' % (self.email)


class SiteUser(models.Model):
    user = models.OneToOneField(User)
    contact = models.ForeignKey('Contact', unique=True, null=True)
    
    def __unicode__(self):
        return '%s <%s>' % (self.user.username, self.contact.email)
    	
class Member(models.Model):
    lastname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    interests = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey('SiteUser')
    contact = models.ForeignKey('Contact', unique=True)
    
    def __unicode__(self):
        return '%s %s' % (self.firstname, self.lastname)
		
class Club(models.Model):
    name = models.CharField(max_length=40, unique=True)
    type = models.CharField(max_length=40, blank=True, null=True)
    location = models.CharField(max_length=40, blank=True, null=True)
    membercount = models.IntegerField()
    created = models.DateField()
    recruiting = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey('SiteUser')
    contact = models.ForeignKey('Contact', unique=True)
    
    def __unicode__(self):
        return '%s' % (self.name)


class Membership(models.Model):
    joined = models.DateField()
    lastpaid = models.DateField(blank=True, null=True)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')
	
    def __unicode__(self):
        return '%s belongs to %s' % (self.member, self.club)
	
	
