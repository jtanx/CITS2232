from django.db import models

class User(models.Model):
    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=40)
    lastname = models.CharField(max_length=40, blank=True, null=True)
    firstname = models.CharField(max_length=40, blank=True, null=True)
    contact_id = models.IntegerField()
    registered = models.DateField()
    usertype = models.IntegerType()
    contact = models.ForeignKey('Contact')
    
    def __unicode__(self):
    	return '%s' % (self.username)
    	
class Contact(models.Model):
	email = models.CharField(max_length=40)
	address = models.CharField(max_length=255, blank=True, null=True)
	facebook = models.CharField(max_length=40, blank=True, null=True)
	twitter = models.CharField(max_length=40, blank=True, null=True)
	phone = models.CharField(max_length=40, blank=True, null=True)
	fax = models.CharField(max_length=40, blank=True, null=True)
	
	def __unicode__(self):
		return '%s' % (self.id) #is this allowed? id is not defined above but it will be...
		
class Member(models.Model)
	lastname = models.CharField(max_length=40)
	firstname = models.CharField(max_length=40)
	contact_id = models.IntegerField()
	owner_id = models.IntegerField()
	interests = models.CharField(max_length=255, blank=True, null=True)
	owner = models.ForeignKey('User')
	contact = models.ForeignKey('Contact')
	
	def __unicode__(self):
		return '%s %s' % (self.firstname, self.lastname)
		
class Club(models.Model)
	name = models.CharField(max_length=40, unique=True)
	type = models.CharField(max_length=40, blank=True, null=True)
	location = models.CharField(max_length=40, blank=True, null=True)
	membercount = models.IntegerField()
	created = models.DateField()
	recruiting = models.BoolenField(default=True)
	description = models.CharField(max_length=255, blank=True, null=True)
	contact_id = models.IntegerField(blank=True, null=True) #should this be allowed to be null?
	owner_id = models.IntegerField()
	owner = models.ForeignKey('User')
	contact = models.ForeignKey('Contact')
	
	def __unicode__(self):
		return '%s %s' % (self.name)
		
class Membership(models.Model)
	member_id = models.IntegerField()
	club_id = models.IntegerField()
	joined = models.DateField()
	lastpaid = models.DateField(blank=True, null=True)
	member = models.ForeignKey('Member')
	club = models.ForeignKey('Club')
	
	def __unicode__(self):
		return '%s belongs to %s' % (self.member, self.club)
	
	