from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_delete
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

class Member(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
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

    @staticmethod
    def club_created(sender, instance, created, **kwargs):
        '''Auto increments the club count for a club type
           when a club is created'''
        if created and instance.type:
            instance.type.club_count += 1
            instance.type.save()

    @staticmethod
    def club_updated(sender, instance,  **kwargs):
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

    @staticmethod
    def club_deleted(sender, instance, **kwargs):
        '''Auto updates club count when clubs are deleted'''
        if instance.type:
            instance.type.club_count -= 1
            instance.type.save()

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
    contact = models.ForeignKey(Member, blank=True, null=True,\
                                on_delete=models.SET_NULL)
    description = models.CharField(max_length=255)
    facebook = models.CharField(max_length=40, blank=True, null=True)
    twitter = models.CharField(max_length=40, blank=True, null=True)
    owner = models.ForeignKey(User)
    
    def __unicode__(self):
        return '%s' % (self.name)

post_save.connect(ClubType.club_created, sender=Club)
pre_save.connect(ClubType.club_updated, sender=Club)
post_delete.connect(ClubType.club_deleted, sender=Club)

class Membership(models.Model):
    joined = models.DateField(default=datetime.now)
    last_paid = models.DateField(blank=True, null=True)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')

    class Member:
        unique_together = (("member", "club"),)
	
    def __unicode__(self):
        return '%s belongs to %s' % (self.member, self.club)

class UserMeta(models.Model):
    user = models.ForeignKey(User)
    member_count = models.IntegerField(default=0)
    membership_count = models.IntegerField(default=0)
    club_count = models.IntegerField(default=0)

    @staticmethod
    def member_created(sender, instance, created, **kwargs):
        if created:
            meta, created = UserMeta.objects.get_or_create(user=instance.owner)
            meta.member_count += 1
            meta.save()

    @staticmethod
    def member_deleted(sender, instance, **kwargs):
        try:
            meta = UserMeta.objects.get(user=instance.owner)
        except ObjectDoesNotExist:
            return
        
        meta.member_count -= 1
        meta.save()

    @staticmethod
    def membership_created(sender, instance, created, **kwargs):
        if created:
            user = instance.member.owner
            meta, created = UserMeta.objects.get_or_create(user=user)
            meta.membership_count += 1
            meta.save()

    @staticmethod
    def membership_deleted(sender, instance, **kwargs):
        try:
            user = instance.member.owner
            meta = UserMeta.objects.get(user=user)
        except ObjectDoesNotExist:
            return

        meta.membership_count -= 1
        meta.save()

    @staticmethod
    def club_created(sender, instance, created, **kwargs):
        if created:
            meta, created = UserMeta.objects.get_or_create(user=instance.owner)
            meta.club_count += 1
            meta.save()

    @staticmethod
    def club_updated(sender, instance,  **kwargs):
        '''Auto updates club counts if a club type is changed'''
        if instance.pk:
            old_info = Club.objects.get(pk=instance.pk)
            if old_info.owner != instance.owner:
                UserMeta.club_created(sender, instance, True)
                UserMeta.club_deleted(sender, old_info)

    @staticmethod
    def club_deleted(sender, instance, **kwargs):
        try:
            meta = UserMeta.objects.get(user=instance.owner)
        except ObjectDoesNotExist:
            return

        meta.club_count -= 1
        meta.save()

post_save.connect(UserMeta.member_created, sender=Member)
post_delete.connect(UserMeta.member_deleted, sender=Member)
post_save.connect(UserMeta.membership_created, sender=Membership)
post_delete.connect(UserMeta.membership_deleted, sender=Membership)
post_save.connect(UserMeta.club_created, sender=Club)
pre_save.connect(UserMeta.club_updated, sender=Club)
post_delete.connect(UserMeta.club_deleted, sender=Club)
        
