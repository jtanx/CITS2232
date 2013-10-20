from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_delete, post_syncdb
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
import urllib, urllib2, json

class LocationManager(models.Manager):
    # Modification of http://goo.gl/cy5OUc
    # More based on http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
    def nearby_locations(self, latitude, longitude, radius, max_results=40):
        '''Determines all clubs within a set range, given in kilometres'''
        distance_unit = 6371
        if not latitude or not longitude:
            return self.filter(id_in=[])
        
        from django.db import connection, transaction
        from django.conf import settings
        import math
        cursor = connection.cursor()
        
        def acos(x):
            #print('acos(x)', x)
            if x is None: return None
            elif x <= -1: return math.pi
            elif x >= 1: return 0
            else: return math.acos(x)
        def cos(x):
            #print('cos(x)', x)
            if x is None: return None
            return math.cos(x)
        def radians(x):
            #print('radians(x)', x)
            if x is None: return None
            return math.radians(x)
        
        def sin(x):
            #print('sin(x)', x)
            if x is None: return None
            return math.sin(x)
        
        connection.connection.create_function('acos', 1, acos)
        connection.connection.create_function('cos', 1, cos)
        connection.connection.create_function('rad', 1, radians)
        connection.connection.create_function('sin', 1, sin)
     
        #Reference: 
        #http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
        latitude = math.radians(latitude)
        longitude = math.radians(longitude)
        r = 0.1570 / 1000 * radius # 0.1570 per 1000km
        latmin = latitude - r
        latmax = latitude + r
        deltaLong = math.asin(math.sin(r)/math.cos(latitude))
        lonmin = longitude - deltaLong
        lonmax = longitude + deltaLong
        
        
        if latmax > math.pi/2:
            lonmin = -math.pi
            latmax, lonmax = math.pi/2, math.pi
        if latmin < -math.pi/2: 
            latmin, lonmin = -math.pi/2, -math.pi
            lonmax = math.pi
        if lonmin < -math.pi or lonmin > math.pi or lonmax < -math.pi or lonmax > math.pi:
            lonmin, lonmax = -math.pi, math.pi
        
        #Old, unbounded search. Not used anymore
        sql = \
        '''
        SELECT id, (6371 * acos(
          sin(rad(latitude))*sin(%s) +
          cos(rad(latitude))*cos(%s) * cos(rad(longitude) - %s)))
          AS distance
        FROM (
          SELECT id, latitude, longitude
          FROM sportsrec_club
          WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        )
        WHERE distance < %d
        ORDER BY distance LIMIT 0, %d;
        ''' % (latitude, latitude, longitude, int(radius), max_results)
        
        sql2 = \
        '''
        SELECT id
          FROM sportsrec_club
          WHERE (rad(latitude) >= %f AND rad(latitude) <= %f) AND
                (rad(longitude) >= %f AND rad(longitude) <= %f) AND
                acos(sin(%f) * sin(rad(latitude)) + cos(%f) * cos(rad(latitude)) * cos (rad(longitude) - %f)) <= %f
          LIMIT 0, %d
        ''' % (latmin, latmax, lonmin, lonmax, latitude, latitude, longitude, r, max_results)

        cursor.execute(sql2)
        ids = [row[0] for row in cursor.fetchall()]

        return self.filter(id__in=ids)

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
        return '%s %s (%s)' % (self.first_name, self.last_name, self.email)

class ClubTag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return '%s' % (self.name)

class ClubType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=255)
    club_count = models.IntegerField(default=0)
    
    ''' #No signal for you!
    @staticmethod
    def club_created(sender, instance, created, **kwargs):
        #Auto increments the club count for a club type
        #   when a club is created
        if created and instance.type:
            instance.type.club_count += 1
            instance.type.save()

    @staticmethod
    def club_updated(sender, instance,  **kwargs):
        #Auto updates club counts if a club type is changed
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
        #Auto updates club count when clubs are deleted
        try:
            instance.type.club_count -= 1
            instance.type.save()
        except ObjectDoesNotExist:
            #Club type was deleted...
            return'''

    def __unicode__(self):
        return '%s' % (self.name)

class Club(models.Model):
    name = models.CharField(max_length=40, unique=True)
    address = models.CharField(max_length=255)
    objects = models.Manager()
    #location = models.CharField(max_length=40, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    location = LocationManager()
    
    tags = models.ManyToManyField(ClubTag, blank=True, null=True)
    type = models.ForeignKey(ClubType)
    member_count = models.IntegerField(default=0)
    created = models.DateField(default=datetime.now)
    recruiting = models.BooleanField(default=True)
    contact = models.ForeignKey(Member, blank=True, null=True,\
                                on_delete=models.SET_NULL,related_name='member_contact')
    description = models.CharField(max_length=255)
    facebook = models.CharField(max_length=40, blank=True, null=True)
    twitter = models.CharField(max_length=40, blank=True, null=True)
    owner = models.ForeignKey('Member',on_delete=models.SET_NULL, null=True, blank=True,\
                                related_name='member_owner')
    
    def __unicode__(self):
        return '%s' % (self.name)
 
    
class Membership(models.Model):
    joined = models.DateField(default=datetime.now)
    last_paid = models.DateField(blank=True, null=True)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')
    
    '''#No trigger for you!
    @staticmethod
    def membership_created(sender, instance, created, **kwargs):
        if created:
            instance.club.member_count += 1
            instance.club.save()

    @staticmethod
    def membership_deleted(sender, instance, **kwargs):
        try:
            instance.club.member_count -= 1
            instance.club.save()
        except ObjectDoesNotExist:
            #Club or member no longer exists.
            #As owner/contact is fk, they're nulled on member delete
            return
    '''
    class Meta:
        unique_together = (("member", "club"),)
    
    def __unicode__(self):
        return '%s belongs to %s' % (self.member, self.club)

class MembershipApplication(models.Model):
    applied = models.DateField(default=datetime.now)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')
    rejected = models.BooleanField(default=False)
    
    class Meta:
        unique_together = (("member", "club"),)
    
    def __unicode__(self):
        return '%s to %s' % (self.member, self.club)

        
#sqlite triggers can't be loaded via custom sql. gg
#https://code.djangoproject.com/ticket/4374        
membership_triggers = \
'''
DROP TRIGGER IF EXISTS MembershipCreated;
DROP TRIGGER IF EXISTS MembershipDeleted;

CREATE TRIGGER MembershipCreated
AFTER INSERT ON sportsrec_membership
FOR EACH ROW
BEGIN
UPDATE sportsrec_club
SET member_count=member_count+1
WHERE id=New.club_id;
END;

CREATE TRIGGER MembershipDeleted
AFTER DELETE ON sportsrec_membership
FOR EACH ROW
BEGIN
UPDATE sportsrec_club
SET member_count=member_count-1
WHERE id=Old.club_id;

UPDATE sportsrec_club
SET owner_id=NULL
WHERE id=Old.club_id AND owner_id=Old.member_id;

UPDATE sportsrec_club
SET contact_id=NULL
WHERE id=Old.club_id AND contact_id=Old.member_id;
END;
'''

club_triggers = \
'''
DROP TRIGGER IF EXISTS ClubCreated;
DROP TRIGGER IF EXISTS ClubUpdated;
DROP TRIGGER IF EXISTS ClubDeleted;

CREATE TRIGGER ClubCreated
AFTER INSERT ON sportsrec_club
FOR EACH ROW
BEGIN
UPDATE sportsrec_clubtype
SET club_count=club_count+1
WHERE id=New.type_id;
END;

CREATE TRIGGER ClubUpdated
AFTER UPDATE OF type_id ON sportsrec_club 
FOR EACH ROW
BEGIN
UPDATE sportsrec_clubtype
SET club_count=club_count+1
WHERE id=New.type_id;

UPDATE sportsrec_clubtype
SET club_count=club_count-1
WHERE id=Old.type_id;
END;

CREATE TRIGGER ClubDeleted
AFTER DELETE ON sportsrec_club
FOR EACH ROW
BEGIN
UPDATE sportsrec_clubtype
SET club_count=club_count-1
WHERE id=Old.type_id;
END;

--no signal for you!
'''

def a_hack_to_load_sqlite_triggers_just_because(created_models, **kwargs):
    cursor = connection.cursor()
    cursor.executescript(membership_triggers)
    cursor.executescript(club_triggers)

#herp derp
post_syncdb.connect(a_hack_to_load_sqlite_triggers_just_because)

'''
#No signals!!! stupidity ensues
#For club counting by type
post_save.connect(ClubType.club_created, sender=Club)
pre_save.connect(ClubType.club_updated, sender=Club)
post_delete.connect(ClubType.club_deleted, sender=Club)
#For membership tracking
post_save.connect(Membership.membership_created, sender=Membership)
post_delete.connect(Membership.membership_deleted, sender=Membership)
#For keeping track of user stats. May not be needed
'''

'''post_save.connect(UserMeta.member_created, sender=Member)
post_delete.connect(UserMeta.member_deleted, sender=Member)
post_save.connect(UserMeta.membership_created, sender=Membership)
post_delete.connect(UserMeta.membership_deleted, sender=Membership)
post_save.connect(UserMeta.club_created, sender=Club)
pre_save.connect(UserMeta.club_updated, sender=Club)
post_delete.connect(UserMeta.club_deleted, sender=Club)'''
        
