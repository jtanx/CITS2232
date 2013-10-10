from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_delete
from datetime import datetime

class Member(models.Model):
    last_name = models.CharField(max_length=40)
    first_name = models.CharField(max_length=40)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=40, blank=True, null=True)
    twitter = models.CharField(max_length=40, blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    interests = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(User)
    
    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

class ClubGroup(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=255)
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.description)

class ClubType(models.Model):
    group = models.ForeignKey(ClubGroup)
    sub_type = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=255)
    club_count = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s (%s)' % (self.sub_type, self.group.name)

class Club(models.Model):
    name = models.CharField(max_length=40, unique=True)
    address = models.CharField(max_length=255)
    location = models.CharField(max_length=40, blank=True, null=True)

    type = models.ForeignKey(ClubType)
    member_count = models.IntegerField(default=1)
    created = models.DateField(default=datetime.now)
    recruiting = models.BooleanField(default=False)
    contact = models.ForeignKey(Member)
    description = models.CharField(max_length=255)
    facebook = models.CharField(max_length=40, blank=True, null=True)
    twitter = models.CharField(max_length=40, blank=True, null=True)
    owner = models.ForeignKey(User)
    
    def __unicode__(self):
        return '%s' % (self.name)

def initClubCount(sender, instance, created, **kwargs):
    '''Auto increments the club count for a club type when a club is created'''
    if created and instance.type:
        instance.type.club_count += 1
        instance.type.save()

def updateClubCount(sender, instance,  **kwargs):
    '''Auto updates club counts if a club type is changed'''
    if instance.pk:
        old_info = Club.objects.get(pk=instance.pk)
        if old_info.type != instance.type:
            if old_info.type:
                old_info.type.club_count -= 1
                old_info.type.save()
            if instance.type:
                instance.type.club_count += 1
                instance.type.save()

def decClubCount(sender, instance, **kwargs):
    '''Auto updates club count when clubs are deleted'''
    if instance.type:
        instance.type.club_count -= 1
        instance.type.save()

post_save.connect(initClubCount, sender=Club)
pre_save.connect(updateClubCount, sender=Club)
post_delete.connect(decClubCount, sender=Club)

class Membership(models.Model):
    joined = models.DateField(default=datetime.now)
    last_paid = models.DateField(blank=True, null=True)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')

    class Member:
        unique_together = (("member", "club"),)
	
    def __unicode__(self):
        return '%s belongs to %s' % (self.member, self.club)
