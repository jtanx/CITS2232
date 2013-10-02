from django.db import models

#Contact must be before User so the foreign key constraint is generated
class Contact(models.Model):
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


class User(models.Model):
    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=40)
    lastname = models.CharField(max_length=40, blank=True, null=True)
    firstname = models.CharField(max_length=40, blank=True, null=True)
    registered = models.DateField()
    usertype = models.IntegerField()
    contact = models.ForeignKey('Contact')
    
    def __unicode__(self):
        return '%s <%s>' % (self.username, self.contact.email)
    	
class Member(models.Model):
    lastname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    interests = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey('User')
    contact = models.ForeignKey('Contact')
    
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
    owner = models.ForeignKey('User')
    contact = models.ForeignKey('Contact')
    
    def __unicode__(self):
        return '%s' % (self.name)


class Membership(models.Model):
    joined = models.DateField()
    lastpaid = models.DateField(blank=True, null=True)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')
	
    def __unicode__(self):
        return '%s belongs to %s' % (self.member, self.club)
	
	
